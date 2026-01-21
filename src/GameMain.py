import pygame, sys, random, time, numpy, os
import pygame.sndarray
from constant import *
from Ball import Ball
from Paddle import Paddle
from Particle import Particle

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class GameMain:
    def __init__(self):
        pygame.init()   

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.sound_channel_1 = pygame.mixer.Channel(0)
        self.sound_channel_2 = pygame.mixer.Channel(1)
        self.sound_channel_3 = pygame.mixer.Channel(2)
        self.sound_channel_1.set_volume(0.5)
        self.sound_channel_2.set_volume(0.35)
        self.sound_channel_3.set_volume(0.75)
        
        self.sounds_list = {
            'paddle_hit': pygame.mixer.Sound(resource_path('assets/paddle_hit.wav')),
            'score': pygame.mixer.Sound(resource_path('assets/score.wav')),
            'wall_hit': pygame.mixer.Sound(resource_path('assets/wall_hit.wav')),
            'intro': pygame.mixer.Sound(resource_path('assets/intro.wav')),
            'enter': pygame.mixer.Sound(resource_path('assets/enter.wav')),
            'serve': pygame.mixer.Sound(resource_path('assets/serve.wav')),
            'victory': pygame.mixer.Sound(resource_path('assets/victory.wav')),
            'defeat': pygame.mixer.Sound(resource_path('assets/defeat.wav'))
        }

        self.small_font = pygame.font.Font(resource_path('assets/font.ttf'), 24)
        self.medium_font = pygame.font.Font(resource_path('assets/font.ttf'), 36)
        self.large_font = pygame.font.Font(resource_path('assets/font.ttf'), 48)
        self.score_font = pygame.font.Font(resource_path('assets/font.ttf'), 96)
        self.title_font = pygame.font.Font(resource_path('assets/font.ttf'), 128)

        self.player1_score = 0
        self.player2_score = 0

        self.serving_player = 1
        self.winning_player = 0

        self.player1 = Paddle(self.screen, 30, HEIGHT/2 - PADDLE_HEIGHT/2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.player2 = Paddle(self.screen, WIDTH - 45, HEIGHT/2 - PADDLE_HEIGHT/2, PADDLE_WIDTH, PADDLE_HEIGHT)

        self.ball = Ball(self.screen, WIDTH/2 - 6, HEIGHT/2 - 6, 12, 12)

        self.game_state = 'start'
        self.multiplayer_mode = DEBUG_MULTIPLAYER
        self.ai_difficulty = 'weak'
        if DEBUG_FORCE_STRONG_AI:
            self.ai_difficulty = 'strong'

        self.ai_update_delay = random.uniform(AI_UPDATE_DELAY_MIN, AI_UPDATE_DELAY_MAX) 
        self.ai_last_update_time = 0
        self.ai_target_y = None
        self.ai_prediction_error_factor = random.uniform(AI_PREDICTION_ERROR_MIN, AI_PREDICTION_ERROR_MAX)
        self.ai_last_ball_y_direction = 0  
        self.ai_needs_recalculation = False

        self.particles = []
        
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_time_remaining = 0

        self.sound_channel_3.play(self.sounds_list['intro'])

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == 'start':
                        self.sound_channel_3.play(self.sounds_list['enter'])
                        self.game_state = 'serve'
                    elif self.game_state == 'serve':
                        self.sound_channel_3.play(self.sounds_list['serve'])
                        self.game_state = 'play'
                    elif self.game_state == 'done':
                        self.game_state = 'serve'
                        self.ball.Reset()
                        self.player1_score = 0
                        self.player2_score = 0
                        if self.winning_player == 1:
                            self.serving_player = 2
                        else:
                            self.serving_player = 1
                elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    if self.game_state == 'start' or self.game_state == 'done':
                        # Toggle multiplayer mode
                        self.multiplayer_mode = not self.multiplayer_mode
                        self.sound_channel_3.play(self.sounds_list['enter'])
                        if self.game_state == 'start':
                            self.game_state = 'serve'
                        elif self.game_state == 'done':
                            self.game_state = 'serve'
                            self.ball.Reset()
                            self.player1_score = 0
                            self.player2_score = 0
                            if self.winning_player == 1:
                                self.serving_player = 2
                            else:
                                self.serving_player = 1

        if self.game_state == 'serve':
            self.ball.dy = random.uniform(SERVE_BALL_DY_MIN, SERVE_BALL_DY_MAX)
            new_ball_dx = random.uniform(SERVE_BALL_DX_MIN, SERVE_BALL_DX_MAX)
            if self.serving_player == 1:
                self.ball.dx = new_ball_dx
            else:
                self.ball.dx = -new_ball_dx

        elif self.game_state == 'play':

            # In case ball is stuck, moves it
            if self.ball.dx == 0:
                self.ball.dy = random.uniform(SERVE_BALL_DY_MIN, SERVE_BALL_DY_MAX)
                new_ball_dx = random.uniform(SERVE_BALL_DX_MIN, SERVE_BALL_DX_MAX)
                if self.serving_player == 1:
                    self.ball.dx = new_ball_dx
                else:
                    self.ball.dx = -new_ball_dx

            # ball hit player paddle
            player1_collision = self.ball.Collides(self.player1)
            player2_collision = self.ball.Collides(self.player2)
            if (player1_collision and self.ball.dx < 0) or (player2_collision and self.ball.dx > 0):
                self.sound_channel_1.play(self.PitchShift(self.sounds_list['paddle_hit'], self.GetPitchFactor(self.ball.dx)))
                self.ball.dx = -self.ball.dx * REFLECT_DX_MULTIPLIER
                if abs(self.ball.dx) > BALL_TERMINAL_DX:
                    if self.ball.dx < 0:
                        self.ball.dx = -BALL_TERMINAL_DX
                    else:
                        self.ball.dx = BALL_TERMINAL_DX
                
                # Calculate new dy based on where the ball hit the paddle
                if player1_collision:
                    paddle = self.player1
                else:
                    paddle = self.player2
                
                # Calculate offset from paddle center (-1 to 1, where 0 is center)
                ball_center_y = self.ball.rect.y + self.ball.rect.height / 2
                paddle_center_y = paddle.rect.y + paddle.rect.height / 2
                offset = (ball_center_y - paddle_center_y) / (paddle.rect.height / 2)
                
                # Clamp offset to [-1, 1] range
                offset = max(-1, min(1, offset))
                
                # Map offset to dy velocity (steeper angle at edges, flatter at center)
                new_ball_dy = offset * REFLECT_DY_MAX
                self.ball.dy = new_ball_dy
                
                if player1_collision:
                    self.DrawParticles((self.ball.rect.x, self.ball.rect.y), 'normal', 'right', 8)
                else:
                    self.DrawParticles((self.ball.rect.x, self.ball.rect.y), 'normal', 'left', 8)

            # ball hit top wall
            if self.ball.rect.y <= 0 and self.ball.dy < 0:
                self.DrawParticles((self.ball.rect.x, self.ball.rect.y), 'normal', 'down', 12)
                self.ball.rect.y = 1  # Push ball slightly away from wall to prevent sticking
                self.ball.dy = abs(self.ball.dy)  # Ensure positive velocity (moving down)
                # Ensure minimum bounce velocity to prevent getting stuck
                if abs(self.ball.dy) < 50:
                    self.ball.dy = 50
                self.sound_channel_2.play(self.sounds_list['wall_hit'])
                # Trigger AI recalculation after reflection
                if not DEBUG_PERFECT_STRONG_AI:
                    self.ai_needs_recalculation = True

            # ball hit bottom wall
            if self.ball.rect.y >= HEIGHT - 12 and self.ball.dy > 0:
                self.DrawParticles((self.ball.rect.x, self.ball.rect.y), 'normal', 'up', 12)
                self.ball.rect.y = HEIGHT - 13  # Push ball slightly away from wall to prevent sticking
                self.ball.dy = -abs(self.ball.dy)  # Ensure negative velocity (moving up)
                # Ensure minimum bounce velocity to prevent getting stuck
                if abs(self.ball.dy) < 50:
                    self.ball.dy = -50
                self.sound_channel_2.play(self.sounds_list['wall_hit'])
                # Trigger AI recalculation after reflection
                if not DEBUG_PERFECT_STRONG_AI:
                    self.ai_needs_recalculation = True

            # ball hit left wall
            if self.ball.rect.x < 0:
                self.DrawParticles((self.ball.rect.x, self.ball.rect.y), 'big', 'right', 24)
                self.serving_player = 1
                self.player2_score += 1
                self.sound_channel_2.play(self.sounds_list['score'])
                if self.player2_score == WINNING_SCORE:
                    self.sound_channel_3.play(self.sounds_list['defeat'])
                    self.game_state = 'done'
                    self.winning_player = 2
                    if not DEBUG_FORCE_STRONG_AI:
                        self.ai_difficulty = 'weak'
                else:
                    self.game_state = 'serve'
                    self.ball.Reset()
                self.player2.dy = 0
                self.ScreenShake()

            # ball hit right wall
            if self.ball.rect.x > WIDTH:
                self.DrawParticles((self.ball.rect.x, self.ball.rect.y), 'big', 'left', 24)
                self.serving_player = 2
                self.player1_score += 1
                self.sound_channel_2.play(self.sounds_list['score'])
                if self.player1_score == WINNING_SCORE:
                    self.sound_channel_3.play(self.sounds_list['victory'])
                    self.game_state = 'done'
                    self.winning_player = 1
                    if self.ai_difficulty == 'weak':
                        self.ai_difficulty = 'strong'
                    elif self.ai_difficulty == 'strong':
                        if not DEBUG_FORCE_STRONG_AI:
                            self.ai_difficulty = 'weak'
                else:
                    self.game_state = 'serve'
                    self.ball.Reset()
                self.player2.dy = 0
                self.ScreenShake()

            # Check for collision with CCD to update the ball position
            future_collision = False
            if self.ball.dx > 0:
                future_collision, i = self.ball.ContinuousCollisionDetect(dt, self.player2)
            elif self.ball.dx < 0:
                future_collision, i = self.ball.ContinuousCollisionDetect(dt, self.player1)
            if future_collision:
                self.ball.update(dt * i / COLLISION_CHECK_STEPS)
            else:
                self.ball.update(dt)

        # Player 1 movement
        key = pygame.key.get_pressed()
        if key[pygame.K_w] or (not self.multiplayer_mode and key[pygame.K_UP]):
            self.player1.dy = -PADDLE_SPEED
        elif key[pygame.K_s] or (not self.multiplayer_mode and key[pygame.K_DOWN]):
            self.player1.dy = PADDLE_SPEED
        else:
            self.player1.dy = 0

        if not self.multiplayer_mode:

            # Player 2 movement
            if self.game_state == 'play':
                # Weak AI movement
                if self.ai_difficulty == 'weak':
                    #Give AI direction if's not moving
                    if self.player2.dy == 0:
                        self.player2.dy = random.choice([PADDLE_SPEED, -PADDLE_SPEED])
                    else:
                        # Randomly switch direction
                        switch_direction_chance = random.uniform(0, 1)
                        if switch_direction_chance <= 0.05:
                            self.player2.dy = -self.player2.dy
                    # Switch direction if AI hit the top or bottom of the screen
                    if (self.player2.rect.y + self.player2.rect.height >= HEIGHT and self.player2.dy > 0) or (self.player2.rect.y <= 0 and self.player2.dy < 0):
                        self.player2.dy = -self.player2.dy

                # Strong AI movement
                elif self.ai_difficulty == 'strong':
                    current_time = time.time()
                    
                    # Force recalculation if ball reflected off wall
                    if self.ai_needs_recalculation:
                        self.ai_needs_recalculation = False
                        # Add reaction delay after reflection
                        if not DEBUG_PERFECT_STRONG_AI:
                            self.ai_update_delay = random.uniform(AI_REFLECTION_REACTION_DELAY_MIN, AI_REFLECTION_REACTION_DELAY_MAX)
                        self.ai_last_update_time = current_time
                    
                    # Check if it's time to update bot's target
                    if current_time - self.ai_last_update_time > self.ai_update_delay:
                        # Prepare next update loop
                        self.ai_last_update_time = current_time
                        if not DEBUG_PERFECT_STRONG_AI:
                            self.ai_update_delay = random.uniform(AI_UPDATE_DELAY_MIN, AI_UPDATE_DELAY_MAX)
                        else:
                            self.ai_update_delay = 0
                        # Predict the ball's future y-position with wall reflections
                        time_to_reach = (self.player2.rect.x - self.ball.rect.x) / abs(self.ball.dx)
                        predicted_y, bounce_count = self.PredictBallPosition(self.ball.rect.y, self.ball.dy, time_to_reach)
                        if not DEBUG_PERFECT_STRONG_AI:
                            # Prepare undershoot/overshoot prediction error
                            self.ai_prediction_error = random.uniform(AI_PREDICTION_ERROR_MIN, AI_PREDICTION_ERROR_MAX)
                            # Prepare more prediction error the faster the ball is
                            ball_speed = abs(self.ball.dx)
                            speed_percentage = (ball_speed - SERVE_BALL_DX_MIN) / (BALL_TERMINAL_DX - SERVE_BALL_DX_MIN)
                            if random.uniform(0, 1) < 0.5:
                                speed_error_factor = 1 + (random.uniform(AI_SPEED_PREDICTION_ERROR_MAX/2, AI_SPEED_PREDICTION_ERROR_MAX) * speed_percentage)
                            else:
                                speed_error_factor = 1 - (random.uniform(AI_SPEED_PREDICTION_ERROR_MAX/2, AI_SPEED_PREDICTION_ERROR_MAX) * speed_percentage)
                            
                            # Add prediction error based on ball angle (steeper angles = more error)
                            angle_ratio = abs(self.ball.dy) / max(abs(self.ball.dx), 1)  # Vertical/horizontal ratio
                            angle_percentage = min(angle_ratio / 1.5, 1.0)  # Normalize (0=flat, 1=steep)
                            if random.uniform(0, 1) < 0.5:
                                angle_error_factor = 1 + (random.uniform(AI_ANGLE_PREDICTION_ERROR_MAX/2, AI_ANGLE_PREDICTION_ERROR_MAX) * angle_percentage)
                            else:
                                angle_error_factor = 1 - (random.uniform(AI_ANGLE_PREDICTION_ERROR_MAX/2, AI_ANGLE_PREDICTION_ERROR_MAX) * angle_percentage)
                            
                            # Add extra prediction error if ball will bounce off walls
                            reflection_error_factor = 1.0
                            if bounce_count > 0:
                                # More bounces = more error, compounding effect
                                base_reflection_error = random.uniform(AI_REFLECTION_ERROR_MIN, AI_REFLECTION_ERROR_MAX)
                                reflection_error_factor = 1 + (base_reflection_error * bounce_count)
                            
                            # Apply all error factors
                            # Calculate error as offset from predicted position, not multiplier of absolute position
                            total_error_factor = self.ai_prediction_error * speed_error_factor * angle_error_factor * reflection_error_factor
                            # Convert to offset: deviation from perfect prediction
                            error_offset = (predicted_y - HEIGHT/2) * (total_error_factor - 1.0)
                            self.ai_target_y = predicted_y + error_offset
                            
                            # Occasionally try to hit ball at paddle edge for angle control (like human players)
                            if random.uniform(0, 1) < AI_EDGE_POSITIONING_CHANCE:
                                edge_offset = random.choice([PADDLE_HEIGHT * 0.3, -PADDLE_HEIGHT * 0.3])
                                self.ai_target_y += edge_offset
                        else:
                            self.ai_target_y = predicted_y
                    # Bot moves towards the target
                    if self.ai_target_y is not None:
                        paddle_center = self.player2.rect.y + self.player2.rect.height / 2
                        if not DEBUG_PERFECT_STRONG_AI:
                            decisiveness = random.uniform(AI_DECISIVENESS_MIN, AI_DECISIVENESS_MAX)
                        else:
                            decisiveness = 1
                        if self.ai_target_y < paddle_center - 8:
                            self.player2.dy = -PADDLE_SPEED * decisiveness
                        elif self.ai_target_y > paddle_center + 8:
                            self.player2.dy = PADDLE_SPEED * decisiveness
                        else:
                            self.player2.dy = 0

        else:
            key = pygame.key.get_pressed()
            if key[pygame.K_UP]:
                self.player2.dy = -PADDLE_SPEED
            elif key[pygame.K_DOWN]:
                self.player2.dy = PADDLE_SPEED
            else:
                self.player2.dy = 0

        self.player1.update(dt)
        self.player2.update(dt)
        self.UpdateParticles(dt)
        
        # Update screen shake
        if self.shake_time_remaining > 0:
            self.shake_time_remaining -= dt
            if self.shake_time_remaining <= 0:
                self.shake_offset_x = 0
                self.shake_offset_y = 0
            else:
                self.shake_offset_x = random.randint(-SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_INTENSITY)
                self.shake_offset_y = random.randint(-SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_INTENSITY)

    def render(self):
        self.screen.fill((0, 0, 0))

        if self.game_state == 'start':
            t_welcome = self.title_font.render("MojiPong", False, (255, 255, 255))
            text_rect = t_welcome.get_rect(center=(WIDTH / 2 + 10, HEIGHT / 2 - 40))
            self.screen.blit(t_welcome, text_rect)
            t_credit = self.small_font.render("by mojimups", False, (255, 255, 255))
            text_rect = t_credit.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
            self.screen.blit(t_credit, text_rect)
            t_press_enter_begin = self.medium_font.render('Press Spacebar to play solo!', False, (255, 255, 255))
            text_rect = t_press_enter_begin.get_rect(center=(WIDTH / 2, HEIGHT - 140))
            self.screen.blit(t_press_enter_begin, text_rect)
            t_press_alt_mult = self.medium_font.render('Press Alt to play multiplayer!', False, (255, 255, 255))
            text_rect = t_press_alt_mult.get_rect(center=(WIDTH / 2, HEIGHT - 80))
            self.screen.blit(t_press_alt_mult, text_rect)
        else:
            self.DrawMiddleLine()
            if self.game_state == 'serve':
                if not self.multiplayer_mode:
                    if self.serving_player == 1:
                        t_serve = self.small_font.render("You serve!", False, (255, 255, 255))
                    else:
                        t_serve = self.small_font.render("Bot serve!", False, (255, 255, 255))
                else:
                    if self.serving_player == 1:
                        t_serve = self.small_font.render("P1 serve!", False, (255, 255, 255))
                    else:
                        t_serve = self.small_font.render("P2 serve!", False, (255, 255, 255))
                text_rect = t_serve.get_rect(center=(WIDTH/2, 30))
                self.screen.blit(t_serve, text_rect)
                t_enter_serve = self.small_font.render("Press Spacebar to continue!", False, (255, 255, 255))
                text_rect = t_enter_serve.get_rect(center=(WIDTH / 2, 70))
                self.screen.blit(t_enter_serve, text_rect)
                if not self.multiplayer_mode:
                    t_control_hint = self.small_font.render("Move with W/S or Up/Down arrows.", False, (255, 255, 255))
                else:
                    t_control_hint = self.small_font.render("P1: W/S   P2: Up/Down arrows", False, (255, 255, 255))
                text_rect = t_control_hint.get_rect(center=(WIDTH / 2, HEIGHT - 30))
                self.screen.blit(t_control_hint, text_rect)
            elif self.game_state == 'play':
                pass
            elif self.game_state == 'done':
                self.ball.Hide()
                if not self.multiplayer_mode:
                    if self.winning_player == 1:
                        t_win = self.large_font.render("You won!", False, (255, 255, 255))
                    else:
                        t_win = self.large_font.render("Bot won!", False, (255, 255, 255))
                else:
                    if self.winning_player == 1:
                        t_win = self.large_font.render("P1 won!", False, (255, 255, 255))
                    else:
                        t_win = self.large_font.render("P2 won!", False, (255, 255, 255))
                text_rect = t_win.get_rect(center=(WIDTH / 2, 30))
                self.screen.blit(t_win, text_rect)
                t_enter_serve = self.small_font.render("Press Spacebar to restart!", False, (255, 255, 255))
                text_rect = t_enter_serve.get_rect(center=(WIDTH / 2, 80))
                self.screen.blit(t_enter_serve, text_rect)
                if not self.multiplayer_mode:
                    t_alt_serve = self.small_font.render("Press Alt to switch to multiplayer!", False, (255, 255, 255))
                else:
                    t_alt_serve = self.small_font.render("Press Alt to switch to solo!", False, (255, 255, 255))
                text_rect = t_alt_serve.get_rect(center=(WIDTH / 2, 120))
                self.screen.blit(t_alt_serve, text_rect)
            self.DisplayScore()
            self.player2.render()
            self.player1.render()
            self.ball.render()
            for particle in self.particles:
                particle.render(self.screen)
        
        # Apply screen shake if active
        if self.shake_time_remaining > 0:
            temp_surface = self.screen.copy()
            self.screen.fill((0, 0, 0))
            self.screen.blit(temp_surface, (self.shake_offset_x, self.shake_offset_y))

    def DisplayScore(self):
        self.t_p1_score = self.score_font.render(str(self.player1_score), False, (GRAY_OPACITY, GRAY_OPACITY, GRAY_OPACITY))
        self.t_p2_score = self.score_font.render(str(self.player2_score), False, (GRAY_OPACITY, GRAY_OPACITY, GRAY_OPACITY))
        self.screen.blit(self.t_p1_score, (WIDTH/2 - 150, HEIGHT/2 - 42))
        self.screen.blit(self.t_p2_score, (WIDTH/2 + 100, HEIGHT/2 - 42))
    
    def DrawMiddleLine(self):
        each_line_height = 12
        for i in range(6, HEIGHT, each_line_height*2):
            pygame.draw.rect(self.screen, (GRAY_OPACITY, GRAY_OPACITY, GRAY_OPACITY), pygame.Rect(WIDTH/2 - 2, i, 4, each_line_height))

    def DrawParticles(self, position, size, direction, amount):
        for _ in range(amount):
            self.particles.append(Particle(position[0], position[1], size, direction))

    def UpdateParticles(self, dt):
        for particle in self.particles:
            particle.update(dt)
        active_particles = []
        for p in self.particles:
            if p.size > 0.5:
                active_particles.append(p)
        self.particles = active_particles

    def ScreenShake(self):
        self.shake_time_remaining = SCREEN_SHAKE_DURATION

    def PredictBallPosition(self, start_y, dy, time_to_reach):
        y = start_y
        velocity_y = dy
        distance_to_travel = abs(velocity_y * time_to_reach)
        bounce_count = 0
        
        # Simulate ball bouncing off top and bottom walls
        while distance_to_travel > 0:
            if velocity_y > 0:  # Moving down
                distance_to_bottom = HEIGHT - 12 - y
                if distance_to_travel <= distance_to_bottom:
                    y += distance_to_travel
                    break
                else:
                    y = HEIGHT - 12
                    distance_to_travel -= distance_to_bottom
                    velocity_y = -velocity_y
                    bounce_count += 1
            else:  # Moving up
                distance_to_top = y
                if distance_to_travel <= distance_to_top:
                    y -= distance_to_travel
                    break
                else:
                    y = 0
                    distance_to_travel -= distance_to_top
                    velocity_y = -velocity_y
                    bounce_count += 1
        
        return y, bounce_count

    def GetPitchFactor(self, ball_dx):
        ball_speed = abs(ball_dx)
        speed_percentage = (ball_speed - SERVE_BALL_DX_MIN) / (BALL_TERMINAL_DX - SERVE_BALL_DX_MIN)
        pitch_factor = PADDLE_HIT_PITCH_MIN + speed_percentage * (PADDLE_HIT_PITCH_MAX - PADDLE_HIT_PITCH_MIN)
        return pitch_factor

    #ChatGPT-generated function
    def PitchShift(self, sound, pitch_factor):
        original_samples = pygame.sndarray.array(sound)
        if len(original_samples.shape) == 1:
            num_channels = 1
            samples = original_samples
        elif len(original_samples.shape) == 2:
            num_channels = original_samples.shape[1]
            samples = original_samples
        else:
            raise ValueError("Unsupported audio format")
        new_length = int(len(samples) / pitch_factor)
        new_samples = numpy.zeros((new_length, num_channels), dtype=samples.dtype)
        indices = numpy.linspace(0, len(samples), new_length, endpoint=False)
        for ch in range(num_channels):
            new_samples[:, ch] = numpy.interp(indices, numpy.arange(len(samples)), samples[:, ch])
        new_sound = pygame.sndarray.make_sound(new_samples.astype(numpy.int16))
        return new_sound
    