#!/usr/bin/env python
"""
Bunch of methods for 2-dimensional and 3-dimensional meshes calculations,
especially speeds, positions, paths and level-topography-handling.
"""

import math

from main import SCREEN_H, SCREEN_W, timer

EPSILON = 0.05
UL, UR, LL, LR = "UL", "UR", "LL", "LR"
UPPER, LOWER, LEFT, RIGHT, DIAGONAL = "UPPER", "LOWER", "LEFT", "RIGHT", "DIAG"
VERTICALLY, HORIZONTALLY = "VERTICALLY", "HORIZONTALLY"


def distance(coord_a: tuple or list, coord_b: tuple or list) -> float:
    """
    Calculate distance between two segment in 2D space.

    :param coord_a: tuple -- (x, y) coords of first point
    :param coord_b: tuple -- (x, y) coords of second p
    :return: float -- 2-dimensional distance between segment
    """
    return math.hypot(coord_b[0] - coord_a[0], coord_b[1] - coord_a[1])


def calculate_vector_2d(angle: float, scalar: float) -> tuple:
    """
    Calculate x and y parts of the current vector.

    :param angle: float -- angle of the vector
    :param scalar: float -- scalar value of the vector (e.g. speed)
    :return: tuple -- x and y parts of the vector in format: (float, float)
    """
    radians = math.radians(angle)
    change_y = math.cos(radians)
    change_x = math.sin(radians)
    return change_x * scalar, change_y * scalar


def calculate_angle(start: tuple, end: tuple) -> float:
    """
    Calculate angle in direction from 'start' to the 'end' point in degrees.

    :param start: tuple -- start point coordinates (x, y)
    :param end: tuple -- end point coordinates (x, y)
    :return: float -- degrees in range 0-360.
    """
    radians = -math.atan2(end[0] - start[0], end[1] - start[1])
    return math.degrees(radians) % 360


def move_along_vector(start: tuple, velocity: float, target: tuple = None,
                      angle: float = None) -> tuple:
    """
    Create movement vector starting at 'start' point angled in direction of
    'target' point with scalar velocity 'velocity'. Optionally, instead of
    'target' position, you can pass starting 'angle' of the vector.

    Use 'target' position only, when you now the point and do not know the
    angle between two segment, but want quickly calculate position of the
    another point lying on the line connecting two, known segment.

    :param start: tuple -- point from vector starts
    :param target: tuple -- target that vector 'looks at'
    :param velocity: float -- scalar length of the vector
    :param angle: float -- angle of the vector direction
    :return: tuple -- (optional)position of the vector end
    """
    p1 = (start[0], start[1])
    if target:
        p2 = (target[0], target[1])
        rad = math.atan2(p2[0] - p1[0], p2[1] - p1[1])
        angle = math.degrees(rad)
    if target is None and angle is None:
        raise ValueError("You MUST pass target position or vector angle!")

    v = calculate_vector_2d(angle, velocity)

    return p1[0] + v[0], p1[1] + v[1]


def get_intersection(p1: tuple, p2: tuple, p3: tuple, p4: tuple) -> tuple:
    """
    Relatively cheap method of finding segments-intersections.

    :param p1: tuple -- first point of first segment
    :param p2: tuple -- second point of first segment
    :param p3: tuple -- first point of second segment
    :param p4: tuple -- second point of second segment
    :return: tuple -- position of intersection
    """
    x_0 = (p1[1] - p3[1])
    x_1 = (p4[1] - p3[1])
    x_2 = (p1[0] - p3[0])
    x_3 = (p2[0] - p1[0])
    x_4 = (p2[1] - p1[1])
    x_5 = p4[0] - p3[0]

    s = ((x_5 * x_0 - x_1 * x_2) / (x_1 * x_3 - x_5 * x_4))
    return p1[0] + s * x_3, p1[1] + s * x_4


def cross_product(a, b):
    return a[0] * b[0] - b[1] * a[1]


def ccw(points_list: list or tuple) -> bool:
    """
    Check if sequence of points is oriented in clockwise or counterclockwise
    order.
    """
    a, b, c = points_list[0], points_list[1], points_list[2]
    val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
    return val > 0


def are_points_in_line(a, b, c):
    return -EPSILON < (
            distance(a, c) + distance(c, b) - distance(a, b)) < EPSILON


def get_polygon_bounding_box(points_list):
    """
    Helper function for obtaining a bounding box of segment. Allows fast
    checking if two polygons intersects. It is known that if bounding boxes
    of two polygons do not intersect, polygons do not intersect either.
    """
    box = [
        (min([p[0] for p in points_list]), min([p[1] for p in points_list])),
        (max([p[0] for p in points_list]), max([p[1] for p in points_list]))
        ]
    return box


def get_segment_bounding_box(segment: list or tuple) -> list:
    """
    Helper function for obtaining a bounding box of segment. Allows fast
    checking if two segments intersects.

    :param segment: list
    return: tuple of tuples
    """
    box = [
        (min(segment[0][0], segment[1][0]), min(segment[0][1], segment[1][1])),
        (max(segment[0][0], segment[1][0]), max(segment[0][1], segment[1][1]))
        ]
    return box


def do_boxes_intersect(a: tuple, b: tuple, c: tuple, d: tuple) -> bool:
    """
    It is known that if bounding boxes
    of two segments do not intersect, segments do not intersect either.
    """
    return a[0] <= d[0] and b[0] >= c[0] and a[1] <= c[1] <= b[1]


def intersects(segment_a: list or tuple, segment_b: list or tuple) -> bool:
    """
    If segment_a is [A, B] and segment_b is [C, D] then segments intersects if
    [A, B, D] is clockwise and [A, B, C] is counter-clockwise, or vice versa.

    :param segment_a: list of tuples -- segment of first segment
    :param segment_b: list of tuples -- segment of second segment
    :return: bool
    """
    a, b = segment_a
    c, d = segment_b

    if are_points_in_line(a, b, c):
        return True

    bounding_box_a = get_segment_bounding_box((a, b))
    bounding_box_b = get_segment_bounding_box((c, d))
    if not do_boxes_intersect(*bounding_box_a, *bounding_box_b):
        return False

    ccw_abc = ccw((a, b, c))
    ccw_abd = ccw((a, b, d))
    ccw_cdb = ccw((c, d, b))
    ccw_cda = ccw((c, d, a))

    return ccw_abc != ccw_abd and ccw_cdb != ccw_cda


class Light:
    """
    Light is a point which represents a source of light or an observer in
    field-of-view simulation.
    """

    def __init__(self, x: int, y: int, color: tuple, obstacles: list):
        self.origin = x, y
        self.color = color

        # objects considered as blocking FOV/light:
        self.obstacles = obstacles

        # our algorithm does not check against whole polygons-obstacles, but
        # against each of their edges:
        self.border_walls = self.screen_borders_to_walls()
        self.walls = self.border_walls + self.obstacles_to_walls()
        self.walls_centers = self.calculate_walls_centers()
        self.closest_wall = None
        # we need obstacle's corners to emit rays from origin to them:
        self.corners_open_walls = {}
        self.corners_close_walls = {}
        self.corners = self.find_corners()
        self.border_corners = self.get_border_corners()

        self.light_polygon = []

    def move_to(self, x, y):
        self.origin = x, y

    @staticmethod
    def screen_borders_to_walls() -> tuple:
        """
        Screen-borders are outermost boundaries of our visibility-light
        polygon. No ray could surpass them.

        :return: tuple
        """
        north_border = ((SCREEN_H, 0), (SCREEN_H, SCREEN_W))
        east_border = ((SCREEN_H, SCREEN_W), (0, SCREEN_W))
        south_border = ((0, SCREEN_W), (0, 0))
        west_border = ((0, 0), (SCREEN_H, 0))
        return north_border, east_border, south_border, west_border

    def obstacles_to_walls(self) -> tuple:
        """
        Each obstacle should be a polygon, which is a list of segments
        represented by tuples (x, y) ordered counter-clockwise. We detect
        each pair of vertices which belong top same edge of polygon and add
        them as new wall which is later checked if it intersects with
        visibility rays.
        """
        walls = []
        for obstacle in self.obstacles:
            vertex_count = len(obstacle)

            for i in range(vertex_count):
                segment = [obstacle[i]]
                if i < vertex_count - 1:
                    segment.append(obstacle[i + 1])
                else:
                    segment.append(obstacle[0])
                wall = tuple(segment)
                walls.append(wall)
        return tuple(walls)

    def find_corners(self) -> list:
        walls = self.walls
        corners = []

        for wall in walls:
            for vertex in wall:
                if vertex not in corners:
                    corners.append(vertex)
                if wall.index(vertex) == 0:
                    self.corners_open_walls[vertex] = wall
                else:
                    self.corners_close_walls[vertex] = wall
        return corners

    @staticmethod
    def get_border_corners() -> tuple:
        return (SCREEN_H, 0), (SCREEN_H, SCREEN_W), (0, SCREEN_W), (0, 0)

    def calculate_walls_centers(self) -> dict:
        centers = {}

        for wall in self.walls:
            half_length = distance(*wall) / 2
            direction = calculate_angle(*wall)
            center = move_along_vector(wall[0], half_length, angle=-direction)
            centers[wall] = center
        return centers

    def update_visible_polygon(self):
        """
        Field of view or lit area is represented by polygon which is basically
        a list of points. Each frame list is updated accordingly to the
        position of the Light
        """
        origin = self.origin  # point from which we will shot rays

        corners = self.corners[::]

        walls = self.sorted_optimized_walls(origin)

        rays = self.cast_rays_to_corners(origin, corners)

        colliding, offset_rays = self.test_rays_against_walls(corners, origin, rays, walls)

        rays = [r for r in rays if r not in colliding] + offset_rays
        # need to sort rays by their ending angle again because offset_rays
        # are unsorted and pushed at the end of the list:
        rays.sort(key=lambda r: calculate_angle(origin, r[1]))
        self.rays = rays

        # finally, we build a visibility polygon using endpoint of each ray:
        self.light_polygon = [r[1] for r in rays]

    def sorted_optimized_walls(self, origin: tuple) -> list:
        """
        Return wals sorted according to distance to origin and without walls
        which could not be seen/lit up since they are behind some, closer
        walls.
        :param origin: tuple -- (x, y) location of light
        :return: list -- sorted walls without redundant walls
        """
        walls = [w for w in self.walls]
        # sorting walls according to their distance to origin allows for
        # faster finding rays intersections and avoiding iterating through
        # whole list of the walls:
        centers = self.walls_centers
        walls.sort(key=lambda w: distance(origin, centers[w]))
        self.closest_wall = walls[0]
        return walls  # [w for w in walls if w not in hidden]

    def test_rays_against_walls(self, corners, origin, rays, walls):
        colliding = set()  # rays which intersects any wall
        offset_rays = []
        corners_open_walls = self.corners_open_walls
        corners_close_walls = self.corners_close_walls
        for wall in walls:
            for ray in self.filter_rays(origin, rays, wall):
                if ray in colliding:
                    continue
                ending = ray[1]
                # check if it is ray shot at obstacle corner:
                if ending in corners:
                    ray_opens = corners_open_walls[ending]
                    ray_closes = corners_close_walls[ending]
                    both_walls = {ray_opens, ray_closes}
                else:
                    both_walls = None

                if intersects(ray, wall) or intersects(wall, ray):
                    if both_walls is None:  # additional around-corner ray
                        colliding.add(ray)
                        new_ray_end = get_intersection(*ray, *wall)
                        offset_rays.append((origin, new_ray_end))
                    elif wall not in both_walls:
                        colliding.add(ray)
        return colliding, offset_rays

    @staticmethod
    def filter_rays(origin: tuple, rays: list, wall: tuple) -> filter:
        """
        Find rays which could intersect with this wall, eg.: orientation of
        their ending to wall starting vertex is clockwise and to ending
        vertex is counterclockwise.

        :param origin: tuple -- light source
        :param rays: list -- all emitted rays
        :param wall: tuple -- current wall to test against
        :return: Iterator -- filtered rays
        """
        first_step = filter(lambda r: ccw((origin, wall[1], r[1])), rays)
        return filter(lambda r: not ccw((origin, wall[0], r[1])), first_step)

    def cast_rays_to_corners(self, origin: tuple, corners: list) -> list:
        """
        Create a 'ray' connecting origin with each corner (obstacle vertex) on
        the screen. Ray is a tuple of two (x, y) coordinates used later to
        find which segment obstructs visibility.
        TODO: find way to emit less offset rays [x][ ]
        :param origin: tuple -- point from which 'light' is emitted
        :param corners: list -- vertices of obstacles
        :return: list -- rays to be tested against obstacles edges
        """
        rays = []
        border_corners = self.border_corners
        corners_open_walls = self.corners_open_walls
        corners_close_walls = self.corners_close_walls

        opened_wall, wall_min_angle, wall_max_angle = None, 0, 360
        wall_start, wall_end = None, None
        for corner in sorted(corners, key=lambda c: calculate_angle(origin, c)):
            angle = calculate_angle(origin, corner)
            begins = corners_open_walls[corner]
            ends = corners_close_walls[corner]

            # this code reduces amount of rays shot at corners to save some
            # processing time by dumping corners which are shadowed by other
            # obstacles:
            if corner not in border_corners:
                if (opened_wall is None
                        or opened_wall in (begins, ends)
                        or not ccw((wall_start, wall_end, corner))):
                    pass
                else:
                    # print("Max angle:", wall_max_angle, "Angle:", angle)
                    if wall_min_angle < angle < wall_max_angle:
                        continue
                        # TODO: make it more efficient [x][ ] important issue #2
                        #  when vertex closing current wall is in LL quadrant
                        #  and checked-against corners are in LR quadrant (their
                        #  angle is not less than max_angle because we 'reset'
                        #  angle at 260 degrees) or vertex opening current wall
                        #  is in LR quadrant and corner is in LL quadrant (its
                        #  angle is larger than in_angle (see update_light_polygon
                        #  method) in filter builtin, ray is shot which should
                        #  not be! (temporary fix: replace filter() wit raw rays
                        #  list (slow!)
                if not ccw((origin, corner, begins[1])):
                    opened_wall = begins
                else:
                    opened_wall = ends

                wall_start, wall_end = opened_wall[0], opened_wall[1]

                wall_min_angle = calculate_angle(origin, wall_start)
                wall_max_angle = calculate_angle(origin, wall_end)

            ray = (origin, corner)
            new_rays = []

            # additional rays to search behind the corners:
            end_a = move_along_vector(origin, 1500,
                                      angle=-angle + EPSILON)
            end_b = move_along_vector(origin, 1500,
                                      angle=-angle - EPSILON)
            offset_ray_a, offset_ray_b = None, None

            if ccw((origin, corner, begins[1])):
                offset_ray_a = (origin, end_b)
            if not ccw((origin, corner, ends[0])):
                offset_ray_b = (origin, end_a)

            for r in (offset_ray_a, ray, offset_ray_b):
                if r is not None:
                    new_rays.append(r)
            rays.extend(new_rays)
        return rays