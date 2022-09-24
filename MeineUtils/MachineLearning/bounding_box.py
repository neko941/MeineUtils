import os
import cv2
import numpy as np
from pathlib import Path
from xml.dom import minidom

class BoundingBoxConverter():
    def __init__(self) -> None:
        """ Pascal VOC Format """
        self.xTopLefts = []
        self.yTopLefts = []
        self.xBottomRights = []
        self.yBottomRights = []

        """ COCO Format """
        self.widthBBoxes = []
        self.heightBBoxes = []

        """ YOLO Format """
        self.xCenterScaled = []
        self.yCenterScaled = []
        self.widthScaled = []
        self.heightScaled = []

        """ Image """
        self.width = None
        self.height = None
        self.imagePath = None

        """ Label """
        self.labels = []
        self.classes = []
        self.labelDirectory = None
        self.labelFilePath = None
        self.labelFileName = None

    def addLabelDirectory(self, labelDirectory):
        self.labelDirectory = labelDirectory
        return self

    def addlabelFileName(self, labelFileName):
        self.labelFileName = labelFileName
        return self

    def YOLO_to_PascalVOC(self):
        self.xTopLefts.extend([0 if (x - w / 2) * self.width < 0 else int((x - w / 2) * self.width) + 1 for x, w in zip(self.xCenterScaled, self.widthScaled)])
        self.xBottomRights.extend([self.width - 1 if (x + w / 2) * self.width > self.width - 1 else int((x + w / 2) * self.width) + 1 for x, w in zip(self.xCenterScaled, self.widthScaled)])
        self.yTopLefts.extend([0 if (y - h / 2) * self.height < 0 else int((y - h / 2) * self.height) + 1 for y, h in zip(self.yCenterScaled, self.heightScaled)])
        self.yBottomRights.extend([self.height - 1 if (y + h / 2) * self.height > self.height - 1 else int((y + h / 2) * self.height) + 1 for y, h in zip(self.yCenterScaled, self.heightScaled)])

    def PascalVOC_to_YOLO(self):
        self.xCenterScaled.extend([((x1 + x2)/2.0 - 1) * (1./self.width) for x1, x2 in zip(self.xTopLefts, self.xBottomRights)])
        self.yCenterScaled.extend([(x2 - x1) * (1./self.width) for x1, x2 in zip(self.xTopLefts, self.xBottomRights)])
        self.widthScaled.extend([((y1 + y2)/2.0 - 1) * (1./self.height) for y1, y2 in zip(self.yTopLefts, self.yBottomRights)])
        self.heightScaled.extend([(y2 - y1) * (1./self.width) for y1, y2 in zip(self.yTopLefts, self.yBottomRights)])

    def COCO_to_YOLO(self):
        self.xCenterScaled.extend([(2 * x1 + w)/(2 * self.width) for x1, w in zip(self.xTopLefts, self.widthBBoxes)])
        self.yCenterScaled.extend([(2 * y1 + h)/(2 * self.height) for y1, h in zip(self.yTopLefts, self.heightBBoxes)])
        self.widthScaled.extend([w / self.width for w in self.widthBBoxes])
        self.heightScaled.extend([h / self.height for h in self.heightBBoxes])


    def addBoundingBox(self, format, bbox=None, labelFilePath=None):
        if labelFilePath:
            self.labelFilePath = labelFilePath
            self.labelFileName = Path(labelFilePath).stem

        if format.lower().replace(" ", "") == "yolo":
            if labelFilePath and labelFilePath.endswith(".txt"):
                lines = np.array([line.strip().split(" ") for line in open(labelFilePath, "r").readlines()], dtype=float)
            
            elif bbox and isinstance(bbox, list):
                if all(isinstance(i, list) for i in bbox):
                    lines = np.array(bbox, dtype=float)
                elif all(isinstance(i, str) for i in bbox):
                    lines = np.array([i.strip().split(" ") for i in bbox], dtype=float)

            if len(lines[0]) == 4:
                self.xCenterScaled.extend(lines[:, 0])
                self.yCenterScaled.extend(lines[:, 1])
                self.widthScaled.extend(lines[:, 2])
                self.heightScaled.extend(lines[:, 3])
            elif len(lines[0]) == 5:
                self.labels.extend([int(label) for label in lines[:, 0]])
                self.xCenterScaled.extend(lines[:, 1])
                self.yCenterScaled.extend(lines[:, 2])
                self.widthScaled.extend(lines[:, 3])
                self.heightScaled.extend(lines[:, 4])
        
        elif format.lower().replace(" ", "") == "pascalvoc":
            if labelFilePath and labelFilePath.endswith(".xml"):
                file = minidom.parse(labelFilePath)
                
                self.labels.extend([l.firstChild.data for l in list(file.getElementsByTagName('name'))])
                self.xTopLefts.extend([int(x1.firstChild.data) for x1 in list(file.getElementsByTagName('xmin'))])
                self.yTopLefts.extend([int(y1.firstChild.data) for y1 in list(file.getElementsByTagName('ymin'))])
                self.xBottomRights.extend([int(x2.firstChild.data) for x2 in list(file.getElementsByTagName('xmax'))])
                self.yBottomRights.extend([int(y2.firstChild.data) for y2 in list(file.getElementsByTagName('ymax'))])

                self.width = int(list(file.getElementsByTagName('width'))[0].firstChild.data)
                self.height = int(list(file.getElementsByTagName('height'))[0].firstChild.data)
            
            elif bbox and isinstance(bbox, list):
                if all(isinstance(i, list) for i in bbox):
                    lines = np.array(bbox, dtype=float)
                elif all(isinstance(i, str) for i in bbox):
                    lines = np.array([i.strip().split(" ") for i in bbox], dtype=float)

            if len(lines[0]) == 4:
                self.xTopLefts.extend(lines[:, 0])
                self.yTopLefts.extend(lines[:, 1])
                self.xBottomRights.extend(lines[:, 2])
                self.yBottomRights.extend(lines[:, 3])
            elif len(lines[0]) == 5:
                self.labels.extend([int(label) for label in lines[:, 0]])
                self.xTopLefts.extend(lines[:, 1])
                self.yTopLefts.extend(lines[:, 2])
                self.xBottomRights.extend(lines[:, 3])
                self.yBottomRights.extend(lines[:, 4])

        return self

    def addImageShape(self, imagePath=None, size=None):
        if imagePath:
            img = cv2.imread(imagePath)[:,:,::-1]
            self.width, self.height = img.shape[1], img.shape[0]
            self.imagePath = imagePath

        if size:
            self.width = size[0]
            self.height = size[1]
        
        return self

    def save(self, format):
        if not self.labelFileName and self.imagePath:
            self.labelFileName = '.'.join(os.path.split(self.imagePath)[1].split('.')[:-1])
        elif not self.labelDirectory and self.labelFilePath:
            self.labelDirectory = os.path.dirname(self.labelFilePath)

        if format.lower() == "yolo":
            file = open(f"{os.path.join(self.labelDirectory, self.labelFileName)}.txt", "w")
            file.writelines([f"{l} {x} {y} {w} {h}\n" for l, x, y, w, h in zip(self.labels, self.xCenterScaled, self.yCenterScaled, self.widthScaled, self.heightScaled)])

        elif format.lower() == "pascalvoc":
            pass

    def addClasses(self, classes):
        if isinstance(classes, list):
            self.classes.extend(classes)

        elif isinstance(classes, str) and classes.endswith(".txt"):
            self.classes.extend([line.replace(" ", "").replace("\n", "").split(",") for line in open(classes, "r").readlines()])
            print(self.classes)
        return self

    def retrieveLabelIndex(self, label):
        return self.classes.index(label)

    def retrieveLabelName(self, label):
        return self.classes[label]

    def changeLabelFormat(self, reverse=False):
        assert self.classes, "Please provide classes using .addClasses before continuing"
        if reverse:
            for index, l in enumerate(self.labels):
                self.labels[index] = self.retrieveLabelName(l) 
        else:
            for index, l in enumerate(self.labels):
                self.labels[index] = self.retrieveLabelIndex(l) 

    def export(self, format, save=False):
        if format.lower() == "pascalvoc":
            if not all([self.xTopLefts, self.yTopLefts, self.xBottomRights, self.yBottomRights]):
                if all([self.xCenterScaled, self.yCenterScaled, self.widthScaled, self.heightScaled]):
                    assert all([self.width, self.height]), "Please provide image shape using .addImageShape before continuing"
                    assert (all([self.xCenterScaled, self.yCenterScaled, self.widthScaled, self.heightScaled]))
                    self.YOLO_to_PascalVOC()

            if save:
                if all(isinstance(x, int) for x in self.labels):
                    self.changeLabelFormat(reverse=True)
                self.save(format=format)

            return self, [(x1, y1, x2, y2) for x1, y1, x2, y2 in zip(self.xTopLefts, self.yTopLefts, self.xBottomRights, self.yBottomRights)]

        elif format.lower() == "yolo":
            if not all([self.xCenterScaled, self.yCenterScaled, self.widthScaled, self.heightScaled]):
                if all([self.xTopLefts, self.yTopLefts, self.xBottomRights, self.yBottomRights]):
                    assert all([self.width, self.height]), "Please provide image shape using .addImageShape before continuing"
                    assert all([self.xTopLefts, self.yTopLefts, self.xBottomRights, self.yBottomRights])
                    self.PascalVOC_to_YOLO()

            if save:
                if all(isinstance(x, str) for x in self.labels):
                    self.changeLabelFormat()
                self.save(format=format)

            return self, [(x, y, w, h) for x, y, w, h in zip(self.xCenterScaled, self.yCenterScaled, self.widthScaled, self.heightScaled)]
