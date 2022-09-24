import os
import cv2
import random
import numpy as np

"""
I yoink from https://blog.paperspace.com/data-augmentation-for-object-detection-rotation-and-shearing/
"""
class RandomRotate(object):
    def __init__(self, angle=None):
        if angle:
            self.angle = angle
        else:
            self.angle = random.randint(1, 359)
        
    def get_enclosing_box(self, corners):
        x_ = corners[:,[0,2,4,6]]
        y_ = corners[:,[1,3,5,7]]
        
        xmin = np.min(x_,1).reshape(-1,1)
        ymin = np.min(y_,1).reshape(-1,1)
        xmax = np.max(x_,1).reshape(-1,1)
        ymax = np.max(y_,1).reshape(-1,1)
        
        final = np.hstack((xmin, ymin, xmax, ymax,corners[:,8:]))
        
        return final

    def bbox_area(self, bbox):
        return (bbox[:,2] - bbox[:,0])*(bbox[:,3] - bbox[:,1])

    def clip_box(self, bbox, clip_box, alpha):
        ar_ = (self.bbox_area(bbox))
        x_min = np.maximum(bbox[:,0], clip_box[0]).reshape(-1,1)
        y_min = np.maximum(bbox[:,1], clip_box[1]).reshape(-1,1)
        x_max = np.minimum(bbox[:,2], clip_box[2]).reshape(-1,1)
        y_max = np.minimum(bbox[:,3], clip_box[3]).reshape(-1,1)
        
        bbox = np.hstack((x_min, y_min, x_max, y_max, bbox[:,4:]))
        
        delta_area = ((ar_ - self.bbox_area(bbox))/ar_)
        
        mask = (delta_area < (1 - alpha)).astype(int)
        
        bbox = bbox[mask == 1,:]


        return bbox

    def rotate_box(self, corners,angle,  cx, cy, h, w):
        corners = corners.reshape(-1,2)
        corners = np.hstack((corners, np.ones((corners.shape[0],1), dtype = type(corners[0][0]))))
        
        M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
        
        
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cx
        M[1, 2] += (nH / 2) - cy
        # Prepare the vector to be transformed
        calculated = np.dot(M,corners.T).T
        
        calculated = calculated.reshape(-1,8)
        
        return calculated

    def get_corners(self, bboxes):
        width = (bboxes[:,2] - bboxes[:,0]).reshape(-1,1)
        height = (bboxes[:,3] - bboxes[:,1]).reshape(-1,1)
        
        x1 = bboxes[:,0].reshape(-1,1)
        y1 = bboxes[:,1].reshape(-1,1)
        
        x2 = x1 + width
        y2 = y1 
        
        x3 = x1
        y3 = y1 + height
        
        x4 = bboxes[:,2].reshape(-1,1)
        y4 = bboxes[:,3].reshape(-1,1)
        
        corners = np.hstack((x1,y1,x2,y2,x3,y3,x4,y4))
        
        return corners

    def rotate_im(self, image, angle):
        # grab the dimensions of the image and then determine the
        # centre
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        return cv2.warpAffine(image, M, (nW, nH))
            
    def __call__(self, img_path, bboxes, save=True):
        img = cv2.imread(img_path)[:,:,::-1]
        w,h = img.shape[1], img.shape[0]
        cx, cy = w//2, h//2
        img = self.rotate_im(img, self.angle)
        corners = self.get_corners(bboxes)
        corners = np.hstack((corners, bboxes[:,4:]))
        corners[:,:8] = self.rotate_box(corners[:,:8], self.angle, cx, cy, h, w)
        new_bbox = self.get_enclosing_box(corners)
        new_bbox = np.array (new_bbox, dtype = float)
        scale_factor_x = img.shape[1] / w
        scale_factor_y = img.shape[0] / h
        img = cv2.resize(img, (w,h))
        new_bbox[:,:4] /= [scale_factor_x, scale_factor_y, scale_factor_x, scale_factor_y] 
        bboxes  = new_bbox
        bboxes = self.clip_box(bboxes, [0,0,w, h], 0.25)

        split_tup = os.path.splitext(img_path)
        save_name = f'{split_tup[0]}-Rotation_{self.angle}{split_tup[1]}'
        if save:
            cv2.imwrite(save_name, cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return img, bboxes, save_name