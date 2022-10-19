import os
import cv2
import numpy as np

"""
I yoink it from https://blog.paperspace.com/data-augmentation-for-object-detection-rotation-and-shearing/
"""
class RandomRotate(object):
    def __init__(self, angle=None):
        if angle:
            self.angle = angle
        else:
            self.angle = np.random.randint(1, 359)
        
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
        save_name = f'{split_tup[0]}-{type(self).__name__}_{self.angle}{split_tup[1]}'
        if save:
            cv2.imwrite(save_name, cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return img, bboxes, save_name

class Augmentation():
    def __init__(self, image_path, label_path):
        self.image_path = image_path
        self.label_path = label_path
        self.image = np.asarray(cv2.imread(self.image_path))

    def copy_label_content(self, new_label_path):
        lines = open(self.label_path, "r").readlines()
        with open(new_label_path, "w") as f:
            for line in lines:
                f.write(line)

    def new_augemented_path(self, path, new_part):
        return f'{".".join(path.split(".")[:-1])}-{new_part}.{path.split(".")[-1]}'
    
    def fix(self, num):
        if int(num) - num == 0: num = int(num)
        return num

    def save(self, image, portion, part):
        cv2.imwrite(self.new_augemented_path(path=self.image_path,
                                                new_part=f"{part}_{portion}"), image)
        self.copy_label_content(new_label_path=self.new_augemented_path(path=self.label_path,
                                                                        new_part=f"{part}_{portion}"))

class RandomValuedImpulseNoise(Augmentation):
    def __init__(self, image_path, label_path, portion=None):
        super().__init__(image_path, label_path)
        if portion == None:
            self.portion = round(np.random.uniform(low=0.001, high=0.1), 3)
        else:
            assert 0 <= portion <= 0.1, "Please use portion within [0, 0.1]"
            self.portion = portion
        self.thres = 1 - self.portion

    def execute(self, save=True):
        mask = np.random.rand(*self.image.shape[:2])
        mask = np.concatenate([mask, mask, mask]).reshape(*mask.shape, 3)
        self.image = np.where(self.portion*2>mask, np.random.randint(low=0, high=255, size=1, dtype=int), self.image) 
        # self.image = np.where(self.portion>mask, 0, self.image)
        # self.image = np.where(self.thres<mask, 255, self.image)
        if save: self.save(image=self.image, 
                           portion=self.portion*2, 
                           part=type(self).__name__)

class RandomSaltAndPepper(Augmentation):
    def __init__(self, image_path, label_path, portion=None):
        super().__init__(image_path, label_path)
        if portion == None:
            self.portion = round(np.random.uniform(low=0.001, high=0.1), 3)
        else:
            assert 0 <= portion <= 0.1, "Please use portion within [0, 0.1]"
            self.portion = portion
        self.thres = 1 - self.portion

    def execute(self, save=True):
        mask = np.random.rand(self.image.shape[0], self.image.shape[1])
        mask = np.array([mask.T, mask.T, mask.T]).T
        self.image = np.where(self.portion>mask, 0, self.image) 
        self.image = np.where(self.thres<mask, 255, self.image)
        if save: self.save(image=self.image, 
                           portion=self.portion*2, 
                           part=type(self).__name__)

class RandomBrightness(Augmentation):
    def __init__(self, image_path, label_path, level=None):
        super().__init__(image_path, label_path)
        if level == None:
            self.level = round(np.random.uniform(low=0.1, high=2), 3)
        else:
            assert 0.1 <= level <= 2, "Please use level within [0.1, 1), (1, 2]"
            self.level = round(float(level), 3)
        
        while self.level == 1:
            self.level = round(np.random.uniform(low=0.1, high=2), 3)
    def execute(self, save=True):
        self.image = np.clip(a=(self.image * self.level).astype(int),
                             a_min=0,
                             a_max=255)
        if save: self.save(image=self.image, 
                           portion=self.level, 
                           part=type(self).__name__)