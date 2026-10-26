# rclone personal backup: privacy notice

This Google OAuth application is for Giovanni's personal use with the local rclone file-transfer tool and machine-bootstrap. It has no public signup or separate hosted storage service.

## Data and permissions

The application requests permission to view and manage all files in the Google Drive account that authorizes it. This allows the local rclone installation to keep using existing backup files after replacing rclone's shared application identity.

The machine-bootstrap workflow uploads encrypted backup archives to the selected Google Drive destination and checks the uploaded copy. It does not automatically delete existing Drive backups. This application adds no analytics or advertising service. File transfers go between the user's computer and Google Drive.

## Credentials and control

Application credentials and Google authorization tokens belong in the user's private rclone configuration, never in this public source repository. The account owner controls the computer, backup destination and archive passphrase.

The account owner can revoke the application's access through Google Account permissions and can manage or delete their Drive files directly. Revoking access stops further authorized transfers; it does not remove files already stored in Drive.

## Source and use

The backup workflow and its instructions are published in this repository. This notice describes a personal backup configuration, not a public cloud-storage service.
