'''
pyStaticMap 0.01
    Copyright 2012 Christian A. Sueiras

    LARGELY Based on the fantastic work of Gerhard Koch <gerhard.koch AT ymail.com>
        http://sourceforge.net/projects/staticmaplite/
        
    -Allows you to generate static maps from OSM data

Depends on:
    -Python Image Library (PIL)
    -URLib2
    
#######################################################################################
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
#######################################################################################
'''
import os
import urllib2
from math import pow, log, tan, pi, cos, floor, ceil
from md5 import md5
import Image
import ImageDraw

class StaticMap:
    def __init__(self):
        self.tile_size = 256
        self.tile_src_url = {   'mapnik' : 'http://tile.openstreetmap.org/%s/%s/%s.png', \
                                'osmarenderer' : 'http://c.tah.openstreetmap.org/Tiles/tile/%s/%s/%s.png', \
                                'cycle' : 'http://c.andy.sandbox.cloudmade.com/tiles/cycle/%s/%s/%s.png' }
                                
        self.tile_default_src = 'mapnik'
        self.marker_base_dir = 'marker_icons'
        
        self.use_tile_cache = True
        self.tile_cache_base_dir = 'cache/tiles'
        
        self.zoom = 0
        self.lat = 0
        self.lon = 0
        self.width = 500
        self.height = 350
        self.markers = []
        self.paths = []
        self.map_type = self.tile_default_src
    
    def setup_map(self, lat, lon, zoom, map_width, map_height):
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
        self.width = int(map_width)
        self.height = int(map_height)
        self.center_x = self.lon_to_tile(self.lon, self.zoom)
        self.center_y = self.lat_to_tile(self.lat, self.zoom)
        
    def lon_to_tile(self, longitude, zoom):
        return ((longitude + 180) / 360) * pow(2, zoom)
        
    def lat_to_tile(self, latitude, zoom):
        return (1 - log(tan(latitude * pi/180) + 1 / cos(latitude * pi/180)) / pi) / 2 * pow(2, zoom)
    

        
    def tile_url_to_filename(self, url):
        return self.tile_cache_base_dir + "/" + url.replace("http://", "")
        
    def check_tile_cache(self, url):
        filename = self.tile_url_to_filename(url)
        if os.path.isfile(filename):
            return filename
        return None
 
    def mkdir_recursive(self, path, mode):
        if not os.path.isdir(os.path.dirname(path)):
            self.mkdir_recursive(os.path.dirname(path), mode)
        try:
            os.mkdir(path, mode)
        except:
            pass
                
    def write_tile_to_cache(self, url, data):
        filename = self.tile_url_to_filename(url)
        self.mkdir_recursive(os.path.dirname(filename), 0777)
        file = open(filename, "w+")
        file.write(data)
        file.close()
        
        return filename
        
    def fetch_tile(self, url):
        if self.use_tile_cache:
            cached = self.check_tile_cache(url)
            if cached != None:
                return cached
        file = urllib2.urlopen(url)
        tile = file.read()

        return self.write_tile_to_cache(url, tile)         
        
    def create_base_map(self):
        self.image = Image.new("RGBA", (self.width, self.height), "#FFFFFF")
        start_x = floor(self.center_x - (self.width / self.tile_size) / 2) - 1
        start_y = floor(self.center_y - (self.height / self.tile_size) / 2) - 1
        end_x = ceil(self.center_x + (self.width / self.tile_size) / 2)
        end_y = ceil(self.center_y + (self.height / self.tile_size) / 2)
        
        center_x_f = floor(self.center_x)
        center_y_f = floor(self.center_y)
        
        self.offset_x = -1 * floor((self.center_x - center_x_f) * self.tile_size)
        self.offset_y = -1 * floor((self.center_y - center_y_f) * self.tile_size)
        
        self.offset_x = self.offset_x + floor(self.width / 2)
        self.offset_y = self.offset_y + floor(self.height / 2)
                
        self.offset_x = self.offset_x + floor(start_x - center_x_f) * self.tile_size
        self.offset_y = self.offset_y + floor(start_y - center_y_f) * self.tile_size

        for x in range(int(start_x), int(end_x+1)):
            for y in range(int(start_y), int(end_y+1)):
                tile_url = self.tile_src_url[self.tile_default_src] % (self.zoom, x, y)
                tile_image_filename = self.fetch_tile(tile_url)
                tile_image = Image.open(tile_image_filename)
                
                dest_x = int((x - start_x) * self.tile_size + self.offset_x)
                dest_y = int((y - start_y) * self.tile_size + self.offset_y)

                self.image.paste(tile_image, (dest_x, dest_y))
                
    def add_marker(self, marker):
        self.markers.append(marker)
    
    def place_markers(self):
        for marker in self.markers:
            marker_lat = marker['lat']
            marker_lon = marker['lon']
            marker_filename = marker['filename']

            marker_offset_x = int(marker['offset_x'])
            marker_offset_y = int(marker['offset_y'])
            
            marker_img = Image.open(self.marker_base_dir + "/" + marker_filename, "r")
            
            dest_x = floor((self.width / 2) - self.tile_size * (self.center_x - self.lon_to_tile(marker_lon, self.zoom)))
            dest_y = floor((self.height / 2) - self.tile_size * (self.center_y - self.lat_to_tile(marker_lat, self.zoom)))

            self.image.paste(marker_img, (int(dest_x + marker_offset_x), int(dest_y + marker_offset_y)))
            
    def point_to_image_point(self, point):
        lon = point['lon']
        lat = point['lat']
        clon = floor((self.width / 2) - self.tile_size * (self.center_x - self.lon_to_tile(lon, self.zoom)))
        clat = floor((self.height / 2) - self.tile_size * (self.center_y - self.lat_to_tile(lat, self.zoom)))
        return (clon, clat)
            
    def add_path(self, point_1, point_2):
        image_point_1 = self.point_to_image_point(point_1)
        image_point_2 = self.point_to_image_point(point_2)
        self.paths.append( (image_point_1, image_point_2) )
    
    def place_paths(self):
        draw = ImageDraw.Draw(self.image)
        for path in self.paths:
            draw.line(path, fill = (255, 0, 128), width=4)
    
    def reset(self):
        self.paths = []
        self.markers = []
    
    def save_map(self, filename):
        self.create_base_map()
        self.place_paths()
        self.place_markers()
        self.image.save(filename, "PNG")