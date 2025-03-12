import os
import shutil

# List of images currently used in the application
used_images = [
    '1f8ecf990061459ebdf2bdb3887afd92_images.jpeg',
    '21826cc038984c65b8139e0d1961ff9f_images_1.jpeg',
    '301242c407974e09ab12cafd9a900e23_images_2.jpeg',
    '6d12a5f2f1c44def9f8555dc0ab1c1bf_images_3.jpeg',
    '38b7ac2f005044aebd814d9505b2bfe5_images_4.jpeg',
    '9d94ad0e13b94224b5d69dca417f2af2_istockphoto-1280875183-612x612.jpg'
]

# Path to the uploads directory
uploads_dir = 'static/uploads'

# Get all files in the uploads directory
all_files = os.listdir(uploads_dir)

# Count of deleted files
deleted_count = 0

# Create a backup directory
backup_dir = 'static/uploads_backup'
os.makedirs(backup_dir, exist_ok=True)

# Delete unused images
for file in all_files:
    if file not in used_images:
        file_path = os.path.join(uploads_dir, file)
        backup_path = os.path.join(backup_dir, file)
        
        # Backup the file before deleting
        shutil.copy2(file_path, backup_path)
        
        # Delete the file
        os.remove(file_path)
        deleted_count += 1
        print(f"Deleted: {file}")

print(f"\nDeleted {deleted_count} unused images.")
print(f"Backup of deleted images saved to {backup_dir}") 