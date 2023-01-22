import os
import shutil

def merge(scr_path, dir_path):
  scr_path=str(scr_path)
  dir_path=str(dir_path)
  try:
    files = next(os.walk(scr_path))[2]
  except Exception as err:
      print(f"Unexpected {err=}, {type(err)=}")
      raise  

  try:
    folders = next(os.walk(scr_path))[1]
  except Exception as err:
      print(f"Unexpected {err=}, {type(err)=}")
      raise  
  for file in files: # Copy the files
    scr_file = scr_path + "/" + file
    dir_file = dir_path + "/" + file
    if os.path.exists(dir_file): # Delete the old files if already exist
      os.remove(dir_file)
    shutil.move(scr_file, dir_file)
  for folder in folders: # Merge again with the subdirectories
    scr_folder = scr_path + "/" + folder
    dir_folder = dir_path + "/" + folder
    if not os.path.exists(dir_folder): # Create the subdirectories if dont already exist
      os.mkdir(dir_folder)
    merge(scr_folder, dir_folder)
  os.rmdir(scr_path)
#path1 = "path/to/folder1"
#path2 = "path/to/folder2"
#
#merge(path1, path2)