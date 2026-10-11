#!/bin/bash

# Array of your 4 images in exact sequential order
images=("image0_starting_point.jpg" "image1.jpg" "image2.jpg" "image04_destination.jpg")

# Array of timestamps incrementing by 5 minutes
times=("13:00:00" "13:07:00" "13:10:00" "13:12:00")

echo "Injecting structured EXIF metadata..."

for i in {0..3}; do
  exiftool -Make="BlackVue" \
           -Model="DR900X Plus Dashcam" \
           -LensModel="BlackVue Ultra-Wide 8M" \
           -LensInfo="2.8mm f/1.8" \
           -FNumber="1.8" \
           -ExposureTime="1/250" \
           -ISO="400" \
           -FocalLength="2.8" \
           -FocalLengthIn35mmFormat="16" \
           -Flash="Off, Did not fire" \
           -ExposureProgram="Action (High-speed)" \
           -ExposureMode="Auto" \
           -ExposureCompensation="0" \
           -MeteringMode="Center-weighted average" \
           -WhiteBalance="Auto" \
           -LightSource="Unknown" \
           -SensingMethod="One-chip color area" \
           -DigitalZoomRatio="1" \
           -XResolution="300" \
           -YResolution="300" \
           -ResolutionUnit="inches" \
           -ColorSpace="sRGB" \
           -Orientation="Horizontal (normal)" \
           -Software="Syndicate Auto-Sync v2.1" \
           -Artist="Samarathunga S.A.J.D.M" \
           -DateTimeOriginal="2026:09:18 ${times[$i]}" \
           -CreateDate="2026:09:18 ${times[$i]}" \
           -ModifyDate="2026:09:18 ${times[$i]}" \
           -SubSecTimeOriginal="14" \
           -SubSecTimeDigitized="14" \
           -OffsetTime="+05:30" \
           -OffsetTimeOriginal="+05:30" \
           -OffsetTimeDigitized="+05:30" \
           -overwrite_original "${images[$i]}"
done

echo "General metadata injection complete."

# Apply GPS coordinates ONLY to the starting point image
echo "Injecting GPS data into starting point..."
exiftool -GPSLatitude=6.854381 -GPSLatitudeRef=N \
         -GPSLongitude=80.078970 -GPSLongitudeRef=E \
         -overwrite_original "image0_starting_point.jpg"

echo "Process finished."
