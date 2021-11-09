"""
Platformer Game

python -m arcade.examples.platform_tutorial.11_animate_character
"""
import arcade
import os

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
TILE_SCALING = 1.0
CHARACTER_SCALING = 1.0
COIN_SCALING = TILE_SCALING
SPRITE_PIXEL_SIZE = 64
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 18
PLAYER_FALL_SPEED = 18

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    """ Player Sprite"""

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.scale = CHARACTER_SCALING

        # Track our state
        self.climbing = False
        self.is_on_ladder = False

        # Jump
        self.can_jump = False
        self.jump_frame = 0

        # Animation
        self.animation_frame = 0
        self.climb_frame = 0

        # Attack
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_mode = 0
        self.next_attack = False

        # --- Load Textures ---

        # Images from Kenney.nl"s Asset Pack 3
        # main_path = "resources/images/animated_characters/female_adventurer/femaleAdventurer"
        # main_path = "resources/images/animated_characters/female_person/femalePerson"
        main_path = "resources/images/animated_characters/male_person/malePerson"
        # main_path = "resources/images/animated_characters/male_adventurer/maleAdventurer"
        # main_path = "resources/images/animated_characters/zombie/zombie"
        # main_path = "resources/images/animated_characters/robot/robot"

        # Load textures for idling
        self.idle_textures = []
        for i in range(4):
            texture = load_texture_pair(f"resources/images/player/adventurer-idle-2-0{i}.png")
            self.idle_textures.append(texture)

        # Load textures for walking
        self.walk_textures = []
        for i in range(6):
            texture = load_texture_pair(f"resources/images/player/adventurer-run3-0{i}.png")
            self.walk_textures.append(texture)

        # Load textures for jumping
        self.jump_textures = []
        for i in range(2):
            texture = load_texture_pair(f"resources/images/player/adventurer-crnr-jmp-0{i}.png")
            self.jump_textures.append(texture)

        # Load textures for falling
        self.fall_textures = []
        for i in range(2):
            texture = load_texture_pair(f"resources/images/player/adventurer-fall-0{i}.png")
            self.fall_textures.append(texture)

        # Load textures for climbing
        self.climb_textures = []
        for i in range(4):
            texture = load_texture_pair(f"resources/images/player/adventurer-ladder-climb-0{i}.png")
            self.climb_textures.append(texture)

        # Load textures for attacking
        self.jump_attack_textures = []
        for i in range(4):
            texture = load_texture_pair(f"resources/images/player/adventurer-air-attack1-0{i}.png")
            self.jump_attack_textures.append(texture)

        self.attack_textures = []
        for j in range(1, 4):
            textures = []
            for i in range((5, 6, 6)[j-1]):
                texture = load_texture_pair(f"resources/images/player/adventurer-attack{j}-0{i}.png")
                textures.append(texture)
            self.attack_textures.append(textures)

        # Set the initial texture
        self.texture = self.idle_textures[0][0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        #self.set_hit_box([[-22, -64], [22, -64], [22, 28], [-22, 28]])
        #self.set_hit_box([[-22, -56], [-10, -56], [-10, -64], [10, -64], [10, -56], [22, -56], [22, 28], [-22, 28]])
        self.set_hit_box([[-27, -40], [-3, -64], [3, -64], [27, -40], [27, 28], [-27, 28]])
        #self.set_hit_box(self.texture.hit_box_points)

    def update(self):
        pass

    def update_animation(self, delta_time: float = 1/60):
        self.animation_frame += 1

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and (abs(self.change_y) > 1 or abs(self.change_x) > 1):
            self.climb_frame += 1
        if self.climbing:
            self.texture = self.climb_textures[self.climb_frame // 4 % 4][self.character_face_direction]
            return

        # Attack animation
        if self.is_attacking:
            if (not self.can_jump) and not self.is_on_ladder:
                if self.attack_mode != 0:
                    self.is_attacking = False
                    self.attack_frame = 0
                    self.attack_mode = 0
                    return
                self.texture = self.jump_attack_textures[self.attack_frame // 4][self.character_face_direction]
                self.attack_frame += 1
                if self.attack_frame >= 4 * 4:
                    self.is_attacking = False
                    self.attack_frame = 0
                    self.attack_mode = 0
                return
            else:
                self.texture = self.attack_textures[self.attack_mode - 1][self.attack_frame // 4][self.character_face_direction]
                self.attack_frame += 1
                self.change_x = 0
                if self.attack_mode == 0:
                    self.is_attacking = False
                    self.attack_frame = 0
                    self.attack_mode = 0
                    return
                if self.attack_frame >= 4 * (5, 6, 6)[self.attack_mode - 1]:
                    self.attack_frame = 0
                    if self.next_attack:
                        self.next_attack = False
                        self.attack_mode += 1
                        return
                    self.is_attacking = False
                    self.attack_mode = 0
                    self.next_attack = False
                    return
                return

        # Jumping animation
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_textures[self.animation_frame // 4 % 2][self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_textures[self.animation_frame // 4 % 2][self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_textures[self.animation_frame // 5 % 4][self.character_face_direction]
            return

        # Walking animation
        self.texture = self.walk_textures[self.animation_frame // 4 % 6][self.character_face_direction]




class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """
        Initializer for the game
        """

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our "physics" engine
        self.physics_engine = None

        self.map_height = 0
        self.map_width = 0

        # Keep track of the score
        self.score = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(
            "resources/sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("resources/sounds/jump1.wav")
        self.game_over = arcade.load_sound("resources/sounds/gameover1.wav")

    def setup(self, map_name, to_id=0):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_bottom_old = 0
        self.view_left = 0
        self.view_left_old = 0

        self.scroll_speed_x = 0
        self.scroll_speed_y = 0

        # Keep track of the score
        self.score = 0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.background_list = [arcade.SpriteList() for i in range(4)]
        self.foreground_list = [arcade.SpriteList() for i in range(4)]
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.door_list = arcade.SpriteList()


        # --- Load in a map from the tiled editor ---
        # Map name
        self.map_name = map_name

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
            "Passable Platforms": {
                "use_spatial_hash": True,
            },
            "Moving Platforms": {
                "use_spatial_hash": False,
            },
            "Ladders": {
                "use_spatial_hash": True,
            },
            "Coins": {
                "use_spatial_hash": True,
            },
        }

        # Parallax
        self.background_parallax_list = [(1,1) for i in range(4)]
        self.foreground_parallax_list = [(1,1) for i in range(4)]

        # Read in the tiled map
        self.my_map = arcade.tilemap.TileMap(f"./resources/tilemaps/{map_name}", TILE_SCALING, layer_options)
        for layer in self.my_map.tiled_map.layers:
            if "Background" in layer.name:
                self.background_parallax_list[int(layer.name[-1])] = (layer.parallax_factor.x, layer.parallax_factor.y)
            if "Foreground" in layer.name:
                self.foreground_parallax_list[int(layer.name[-1])] = (layer.parallax_factor.x, layer.parallax_factor.y)


        # Calculate the right edge of the my_map in pixels
        self.map_width = self.my_map.width * GRID_PIXEL_SIZE
        self.map_height = self.my_map.height * GRID_PIXEL_SIZE

        # -- Platforms
        self.wall_list = self.my_map.sprite_lists.get("Platforms", arcade.SpriteList())

        # Passable Platforms
        self.passable_wall_list = self.my_map.sprite_lists.get("Passable Platforms", arcade.SpriteList())


        for sprite in self.passable_wall_list:
            sprite.can_pass = False
            self.wall_list.append(sprite)

        # -- Moving Platforms
        self.moving_platforms_list = self.my_map.sprite_lists.get("Moving Platforms", arcade.SpriteList())


        for sprite in self.moving_platforms_list:
            self.wall_list.append(sprite)

        # -- Background objects
        self.background_list = [self.my_map.sprite_lists.get(f"Background{i}", arcade.SpriteList()) for i in range(4)]

        # -- Foreground objects
        self.foreground_list =  [self.my_map.sprite_lists.get(f"Foreground{i}", arcade.SpriteList()) for i in range(4)]

        # -- Background objects
        self.ladder_list = self.my_map.sprite_lists.get("Ladders", arcade.SpriteList())

        # -- Coins
        self.coin_list = self.my_map.sprite_lists.get("Coins", arcade.SpriteList())

        # -- Door positions
        self.door_list = self.my_map.sprite_lists.get("Doors", arcade.SpriteList())

        # --- Other stuff
        # Set the background color
        if self.my_map.background_color:
            arcade.set_background_color(self.my_map.background_color)


        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()

        self.to_id = to_id
        for door in self.door_list:
            if int(door.properties.get("id", -1)) == int(self.to_id):
                self.player_sprite.center_x = door.center_x
                self.player_sprite.bottom = door.center_y - 32
                break

        self.player_list.append(self.player_sprite)

        # Create the "physics engine"
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY,
                                                             ladders=self.ladder_list)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        for i in range(1,4)[::-1]:
            self.background_list[i].draw()
        self.wall_list.draw()
        self.ladder_list.draw()
        self.coin_list.draw()
        self.door_list.draw()
        self.player_list.draw()
        for i in range(1,4)[::-1]:
            self.foreground_list[i].draw()


        # Draw our score on the screen, scrolling it with the viewport
        #score_text = f"Score: {self.score}"
        #arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
        #                 arcade.csscolor.BLACK, 18)

        debug_text = f"(x, y) = ({self.player_sprite.left}, {self.player_sprite.bottom})"
        #debug_text = f"{self.player_sprite.attack_mode} {self.player_sprite.attack_frame}, {self.player_sprite.can_jump}"
        #debug_text = f"{self.player_sprite.jump_frame}"

        # Draw hit boxes.
        for wall in self.wall_list:
            if hasattr(wall, 'can_pass') and not wall.can_pass:
                wall.draw_hit_box(arcade.color.BLACK, 3)

        #self.player_sprite.draw_hit_box(arcade.color.RED, 3)

    def update_passable_floor(self):
        for wall_sprite in self.wall_list:
            #print(wall_sprite.top, self.player_sprite.bottom)
            if hasattr(wall_sprite, "can_pass"):
                if wall_sprite.top - 10 <= self.player_sprite.bottom and wall_sprite.can_pass:
                    wall_sprite.can_pass = False
                    wall_sprite.add_spatial_hashes()
                elif wall_sprite.top - 10 > self.player_sprite.bottom and not wall_sprite.can_pass:
                    wall_sprite.can_pass = True
                    wall_sprite.clear_spatial_hashes()

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                self.player_sprite.jump_frame = 0
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        if self.player_sprite.jump_frame < 12:
            if self.up_pressed:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

        self.player_sprite.change_y = max(self.player_sprite.change_y, -PLAYER_FALL_SPEED)
        self.player_sprite.jump_frame += 1

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = min(self.player_sprite.change_x + 0.7, PLAYER_MOVEMENT_SPEED)
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = max(self.player_sprite.change_x - 0.7, -PLAYER_MOVEMENT_SPEED)
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            if self.player_sprite.attack_mode < 3 and not self.player_sprite.is_on_ladder:
                self.player_sprite.is_attacking = True
                self.player_sprite.next_attack = True if self.player_sprite.attack_mode != 0 else False
                if not self.physics_engine.can_jump():
                    self.player_sprite.set_position(self.player_sprite.center_x + 30 * ((-1)**(self.player_sprite.character_face_direction == LEFT_FACING)), self.player_sprite.center_y)
                    self.player_sprite.attack_mode = 0
                elif self.player_sprite.attack_mode == 0:
                    self.player_sprite.attack_mode = 1

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player with the physics engine
        hit_sprite_list = self.physics_engine.update()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = True
        else:
            self.player_sprite.can_jump = False

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        self.coin_list.update_animation(delta_time)
        self.player_list.update_animation(delta_time)

        for i in range(1,4):
            self.background_list[i].update_animation(delta_time)
            self.foreground_list[i].update_animation(delta_time)
            self.background_list[i].move(self.scroll_speed_x*(1-self.background_parallax_list[i][0]), self.scroll_speed_y*(1-self.background_parallax_list[i][1]))
            self.foreground_list[i].move(self.scroll_speed_x*(1-self.foreground_parallax_list[i][0]), self.scroll_speed_y*(1-self.foreground_parallax_list[i][1]))

        # Respawn
        if self.player_sprite.bottom < -128:
            self.setup(self.map_name)

        # Update walls, used with moving platforms
        self.update_passable_floor()
        self.wall_list.update()

        # See if the moving wall hit a boundary and needs to reverse direction.
        for wall in self.wall_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:

            # Figure out how many points this coin is worth
            if "Points" not in coin.properties:
                print("Warning, collected a coin without a Points property.")
            else:
                points = int(coin.properties["Points"])
                self.score += points

            # Remove the coin
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)

        # Door
        if self.down_pressed:
            for door in arcade.check_for_collision_with_list(self.player_sprite, self.door_list):
                if "to_name" in door.properties:
                    self.down_pressed = False
                    self.setup(door.properties["to_name"], door.properties.get("to_id", 0))
                    break


        # --- Manage Scrolling ---
        self.scroll_viewport()

    def scroll_viewport(self):
        '''
        # Track if we need to change the viewport
        changed_viewport = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True
        '''

        self.view_left = self.player_sprite.position[0] - SCREEN_WIDTH // 2

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            #changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            #changed_viewport = True

        if self.view_left < GRID_PIXEL_SIZE:
            self.view_left = GRID_PIXEL_SIZE
        elif self.view_left > self.map_width - SCREEN_WIDTH - GRID_PIXEL_SIZE:
            self.view_left = self.map_width - SCREEN_WIDTH - GRID_PIXEL_SIZE

        if self.view_bottom < 0:
            self.view_bottom = 0
        elif self.view_bottom > self.map_height - SCREEN_HEIGHT:
            self.view_bottom = self.map_height - SCREEN_HEIGHT

        #if changed_viewport:
        if True:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don"t line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


        self.scroll_speed_x = self.view_left - self.view_left_old
        self.scroll_speed_y = self.view_bottom - self.view_bottom_old
        self.view_left_old = self.view_left
        self.view_bottom_old = self.view_bottom


def main():
    """ Main method """
    window = MyGame()
    window.setup("test2.json")
    arcade.run()


if __name__ == "__main__":
    main()
