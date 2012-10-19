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

class StaticMap:
    def __init__(self):
        self.tile_size = 256
        self.tile_src_url = {   'mapnik' : 'http://tile.openstreetmap.org/%s/%s/%s.png', \
                                'osmarenderer' : 'http://c.tah.openstreetmap.org/Tiles/tile/%s/%s/%s.png', \
                                'cycle' : 'http://c.andy.sandbox.cloudmade.com/tiles/cycle/%s/%s/%s.png' }
                                
        self.tile_default_src = 'mapnik'
        self.marker_base_dir = 'images/markers'
        self.osm_logo = 'images/osm_logo.png'
        
        self.use_tile_cache = True
        self.tile_cache_base_dir = 'cache/tiles'
        
        self.use_map_cache = True
        self.map_cache_base_dir = 'cache/maps'
        self.map_cache_id = ''
        self.map_cache_file = None
        self.map_cache_extension = 'png'
        
        self.zoom = 0
        self.lat = 0
        self.lon = 0
        self.width = 500
        self.height = 350
        self.markers = []
        self.map_type = self.tile_default_src
    
    def setup_map(self, lat, lon, zoom, map_width, map_height):
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
        self.width = int(map_width)
        self.height = int(map_height)
        
    def lon_to_tile(self, longitude, zoom):
        return ((longitude + 180) / 360) * pow(2, zoom)
        
    def lat_to_tile(self, latitude, zoom):
        return (1 - log(tan(latitude * pi/180) + 1 / cos(latitude * pi/180)) / pi) / 2 * pow(2, zoom)
    
    def init_coords(self):        
        self.center_x = self.lon_to_tile(self.lon, self.zoom)
        self.center_y = self.lat_to_tile(self.lat, self.zoom)
        
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
        self.image = Image.new("RGB", (self.width, self.height), "#FFFFFF")
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
                
    def make_map(self):
        self.init_coords()
        self.create_base_map()
    
    def save_map(self, filename):
        self.make_map()
        self.image.save(filename, "PNG")