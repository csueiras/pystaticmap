'''
pyStaticMap 0.01 (https://github.com/csueiras/pystaticmap)
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
import sys
from staticmap import StaticMap

if __name__ == "__main__":
    maps = [{'lat': 40.714728, 'lon':-73.998672, 'zoom':14, 'width':250, 'height':250, 'filename': 'new_york.png'},\
            {'lat': 27.790491, 'lon':-81.584473, 'zoom':7, 'width':600, 'height':600, 'filename': 'florida.png'}]
            
    output_dir = 'tests'
    
    my_map = StaticMap()
    for test_map in maps:
        print "Generating... " + test_map['filename']
        my_map.setup_map(lat = test_map['lat'], lon = test_map['lon'], zoom = test_map['zoom'], map_width = test_map['width'], map_height =  test_map['height'])
        my_map.make_map()
        my_map.save_map(output_dir + '/' + test_map['filename'])
        print "Generated"