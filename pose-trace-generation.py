#!/usr/bin/env python
import argparse
import os
import shutil


def parse_arg():    
    parser = argparse.ArgumentParser()

    parser.add_argument("input_path",help="input path for a folder containing the multi-view images for a frame")
    parser.add_argument("output", help="Name of the output video file")
    parser.add_argument('-p', '--pattern', help="type of pattern used",type=int, nargs='+', choices=range(0,26))
    parser.add_argument('-s', help="Starting frame",type=int)
    parser.add_argument('-e', help="Starting frame",type=int)
    parser.add_argument('-pad', help="Size of video to produce, input frame will be padded to reach this size, should be widthxheight")
    parser.add_argument('-crop', help="Size of video to produce, input frame will be cropped to reach this size, should be widthxheight")
    args = parser.parse_args()
    return args

def main() : 
    patterns = {
        0:[1,7,13,19,25],
        1:[11,16,22,23,24,25,20,15,10,5], 
        2:[3,4,9,10,15,20,19,24,23,22,21], 
        3:[1,7,13,19,25,19,13,7,1], 
        4:[1,2,3,9,15,20,25], 
        5:[1,2,3,4,5,10,9,8,7,6,11,12,13,14,15,20,19,18,17,16,21,22,23,24,25],
        6:[1,6,11,16,21,22,17,12,7,2,3,8,13,18,23,24,19,14,9,4,5,10,15,20,25],
        7:[25,20,15,10,5,4,9,14,19,24,23,18,13,8,3,2,7,12,17,22,21,16,11,6,1]
    }
    p = 0
    args = parse_arg()
    if args.pattern :
        if len(args.pattern) == 1 :
            p = args.pattern[0]
            if p >= len(patterns):
                print("ERROR : please choose -p between 0 and {:d}".format(len(patterns)-1))
                p = 0
        else : 
            newKey = len(patterns)
            patterns[newKey] = args.pattern
            p = newKey
    
    print(patterns)

    start_frame = 0
    end_frame = 299
    if args.s :
        start_frame = args.s 
    if args.e :
        end_frame = args.e 
    
    has_pad = False
    if args.pad :
        has_pad = True
        size = args.pad
        size = size.split("x")
        if len(size)==1:
            print("Error size should be given as withxheight")
            has_pad = False
        
        width = int(size[0])
        height = int(size[1])

    has_crop = False
    if args.crop :
        has_crop = True
        size = args.crop
        size = size.split("x")
        if len(size)==1:
            print("Error size should be given as withxheight")
            has_pad = False
        
        width = int(size[0])
        height = int(size[1])

    if args.pad and args.crop:
        print("Error should only use pad or crop, not both")

    full_path = args.input_path

    spl = full_path.split("/")

    if len(spl)==1:
        spl = full_path.split("\\")


    data = "/".join(spl[:-2])


    video_format = args.output.split(".")[-1]

    frames = end_frame - start_frame + 1

    

    pattern = patterns[p]

    frame_per_viewpoint = frames//len(pattern)
    print("frame per viewpoint : ", frame_per_viewpoint)


    temp = data+"/temp"

    if os.path.exists(temp):
        print("------------------------------")
        print(f"raw path: {args.input_path}")
        print(f"split array is: {spl}")
        print(f"temp file path is: {temp}")
        print("------------------------------")
        os.remove(temp)

    os.mkdir(temp)

    for f in range(start_frame, end_frame+1):
        view = (f-start_frame)//frame_per_viewpoint
        if view == len(pattern):
            view -= 1
        view = pattern[view]
        #print("frame {:03d} - view {:03d}".format(f, view))

        orig = full_path %(f, view)

        dest = temp+"/image_{:03d}.png".format(f)
        
        shutil.copyfile(orig, dest)

    if video_format == "yuv":
        cmd_ffmpeg = "ffmpeg -framerate 30 -i "+temp+"/image_%03d.png -pix_fmt yuv420p "
    else:
        cmd_ffmpeg = "ffmpeg -f image2 -framerate 30 -i "+temp+"/image_%03d.png -vcodec libx264 -pix_fmt yuv420p "
    
    if has_pad :
        cmd_ffmpeg += '-vf "pad={:d}:{:d}:(ow-iw)/2:(oh-ih)/2:color=gray" '.format(width,height)
    
    if has_crop :
        cmd_ffmpeg += '-vf "crop={:d}:{:d}" '.format(width,height)

    cmd_ffmpeg += data+"/"+args.output
    os.system(cmd_ffmpeg)

    shutil.rmtree(temp)


if __name__ == "__main__":
    main()




