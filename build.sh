#!/bin/bash

#clean
find . -name '.DS_Store' -type f -delete
# md5
python addons_xml_generator.py

# repo
rm zips/repository.jlippold/*.zip
zip -r zips/repository.jlippold/repository.jlippold-1.0.0.zip repository.jlippold/

# addon
rm zips/plugin.video.ring_doorbell/*.zip
zip -r zips/plugin.video.ring_doorbell/plugin.video.ring_doorbell-1.0.0.zip plugin.video.ring_doorbell/

