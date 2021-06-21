# Importing the dependencies
import json
import sys

import cv2
import numpy as np
import argparse
import os
import time
from pathlib import Path
import imutils


class Framer:

    def __init__(self):
        self.painting = None
        self.frame = None
        self.positions = []
        self.positions2 = []
        self.db = 'utils/db.json'

    def enframe(self, paintining_path, frame_path, resize=0, update_db=False):
        self.resize = resize
        if not os.path.exists(self.db):
            data = {}
            position = self._insert_frame(frame_path, data)
            self.positions = position[0]
            self.positions2 = position[1]
        else:
            with open(self.db, 'r+') as fp:
                data = json.load(fp)
            if frame_path not in data or update_db:
                position = self._insert_frame(frame_path, data)
                self.positions = position[0]
                self.positions2 = position[1]
            else:
                self.positions = data[frame_path][0]
                self.positions2 = data[frame_path][1]

        self.painting = cv2.imread(paintining_path)
        if self.painting is None:
            sys.exit(f'It is not possible to open {self.painting}')

        self.frame = cv2.imread(frame_path)
        if self.frame is None:
            sys.exit(f'It is not possible to open {self.frame}')

        self._frame_it()

        path = Path(__file__).parent
        path = os.path.join(path, '../images/outputs/frames')
        if not os.path.exists(path):
            os.makedirs(path)

        p_name = os.path.split(paintining_path)[-1].split(".")[0]
        f_name = os.path.split(frame_path)[-1].split(".")[0]
        out_path = os.path.join(path, f'{p_name}_{f_name}_{time.time()}.png')
        self._save(out_path)

    def _save(self, out_path):
        if self.resize > 0:
            self.final_image = imutils.resize(self.final_image, width=self.resize)
        cv2.imwrite(out_path, self.final_image)
        print(f"Image saved on [{out_path}]")

    # Mouse callback function
    def _draw_circle(self, event, x, y, flags, params):

        # If event is Left Button Click then store the coordinate in the lists, positions and positions2
        if event == cv2.EVENT_LBUTTONUP:
            cv2.circle(self.frame_tmp, (x, y), 10, (255, 0, 0), -1)
            self.positions.append([x, y])
            if self.count != 3:
                self.positions2.append([x, y])
            elif self.count == 3:
                self.positions2.insert(2, [x, y])
            self.count += 1

    def _get_positions(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('image', self._draw_circle)

        while True:
            cv2.imshow('image', self.frame_tmp)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                break

        cv2.destroyAllWindows()

    def _frame_it(self):
        height, width = self.frame.shape[:2]
        h1, w1 = self.painting.shape[:2]

        pts1 = np.float32([[0, 0], [w1, 0], [0, h1], [w1, h1]])
        pts2 = np.float32(self.positions)

        h, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 5.0)

        im1Reg = cv2.warpPerspective(self.painting, h, (width, height))

        mask2 = np.zeros(self.frame.shape, dtype=np.uint8)

        roi_corners2 = np.int32(self.positions2)

        channel_count2 = self.frame.shape[2]
        ignore_mask_color2 = (255,) * channel_count2

        cv2.fillConvexPoly(mask2, roi_corners2, ignore_mask_color2)

        mask2 = cv2.bitwise_not(mask2)
        masked_image2 = cv2.bitwise_and(self.frame, mask2)

        # Using Bitwise or to merge the two images
        self.final_image = cv2.bitwise_or(im1Reg, masked_image2)

    def _insert_frame(self, frame_path, data):
        self.count = 0
        img = cv2.imread(frame_path)
        if img is None:
            sys.exit(f'It is not possible to open {frame_path}')
        self.frame_tmp = img
        self._get_positions()
        data[frame_path] = [self.positions, self.positions2]

        with open(self.db, 'w') as fp:
            json.dump(data, fp)

        return data[frame_path]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This code wil hep you puting you amazing painting on beautiful frames')
    parser.add_argument('--painting', required=True, type=str)
    parser.add_argument('--frame', required=True, type=str)
    parser.add_argument('--resize', type=int, default=0)
    parser.add_argument('--update_db', action='store_true')
    args = parser.parse_args()

    # create a Framer
    francis = Framer()

    # now, put him to work!
    francis.enframe(args.painting, args.frame, args.resize, args.update_db)





