#!/usr/bin/env sh

# ---- setup feats
# download VQA 2017 training dataset
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Train_mscoco.zip
unzip v2_Questions_Train_mscoco.zip -d feats/train2014
wget http://images.cocodataset.org/zips/train2014.zip
unzip train2014.zip -d feats/
rm -rvf train2014.zip v2_Questions_Train_mscoco.zip

# download VQA 2017 validation dataset
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Val_mscoco.zip
unzip v2_Questions_Val_mscoco.zip -d feats/val2014
wget http://images.cocodataset.org/zips/val2014.zip
unzip val2014.zip -d feats/
rm -rvf val2014.zip v2_Questions_Val_mscoco.zip

# download VQA 2017 testing dataset
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Test_mscoco.zip
unzip v2_Questions_Test_mscoco.zip -d feats/test2015
wget http://images.cocodataset.org/zips/test2015.zip
unzip test2015.zip -d feats/
rm -rvf test2015.zip v2_Questions_Test_mscoco.zip



# ---- setup raw
cp feats/train2014/v2_OpenEnded_mscoco_train2014_questions.json raw/
cp feats/val2014/v2_OpenEnded_mscoco_val2014_questions.json raw/
cp feats/test2015/v2_OpenEnded_mscoco_test2015_questions.json raw/

# download VQA 2017 training annotations
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Annotations_Train_mscoco.zip
unzip v2_Annotations_Train_mscoco.zip -d raw/
rm -rvf v2_Annotations_Train_mscoco.zip

# download VQA 2017 validation annotations
wget https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Annotations_Val_mscoco.zip
unzip v2_Annotations_Val_mscoco.zip -d raw/
rm -rvf v2_Annotations_Val_mscoco.zip
