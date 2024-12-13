"""
Author: ChatGPT 4o
Modified by: Christian Duncan

This code just stitches together the PNG files into an mp4 file for later playback.
"""
import argparse
import glob
from moviepy import ImageSequenceClip

def create_mp4_from_pngs(png_files, output_file, fps, codec):
    """
    Create an MP4 video from a collection of PNG files.
    
    Args:
        png_files (list): List of file paths to the PNG files in order.
        output_file (str): Output file path for the MP4 video.
        fps (int): Frames per second for the video.
        codec (str): Codec to use for the video.
    """
    # Create a video clip from the image sequence
    clip = ImageSequenceClip(png_files, fps=fps)
    
    # Write the clip to an MP4 file
    clip.write_videofile(output_file, codec=codec, fps=fps)

def main():
    parser = argparse.ArgumentParser(description="Create an MP4 video from PNG files.")
    parser.add_argument(
        "files",
        metavar="files",
        nargs="+",
        help="List of PNG files to include in the video, in the desired order."
    )
    parser.add_argument(
        "-output",
        type=str,
        default="output_video.mp4",
        help="Output MP4 file name (default: output_video.mp4)"
    )
    parser.add_argument(
        "-fps",
        type=int,
        default=24,
        help="Frames per second for the video (default: 24)"
    )
    parser.add_argument(
        "-codec",
        type=str,
        default="libx264",
        help="Video codec to use (default: libx264)"
    )

    args = parser.parse_args()

 # Expand wildcards using glob
    expanded_files = []
    for pattern in args.files:
        expanded_files.extend(glob.glob(pattern))
    
    if not expanded_files:
        print("No files matched the given patterns.")
        return

    # Call the video creation function
    create_mp4_from_pngs(sorted(expanded_files), args.output, args.fps, args.codec)
    print(f"Video saved as {args.output}")

if __name__ == "__main__":
    main()
