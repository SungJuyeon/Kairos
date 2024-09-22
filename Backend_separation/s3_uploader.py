import boto3
import logging
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import cv2

# .env 파일 로드
load_dotenv()

# S3 클라이언트 설정
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# S3 버킷 이름 설정
BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

async def upload_to_s3(file_name):
    """
    지정된 파일을 S3 버킷에 업로드하고 썸네일을 생성합니다.
    """
    try:
        # 원본 비디오 업로드
        s3_client.upload_file(file_name, BUCKET_NAME, file_name)
        logging.info(f"파일 {file_name}이 S3 버킷 {BUCKET_NAME}에 성공적으로 업로드되었습니다.")
        
        # 썸네일 생성 및 업로드
        thumbnail_name = f"thumbnail_{file_name.replace('.avi', '.jpg')}"
        create_thumbnail(file_name, thumbnail_name)
        s3_client.upload_file(thumbnail_name, BUCKET_NAME, thumbnail_name)
        logging.info(f"썸네일 {thumbnail_name}이 S3 버킷 {BUCKET_NAME}에 업로드되었습니다.")
        
        # 로컬 파일 삭제
        os.remove(file_name)
        os.remove(thumbnail_name)
        logging.info(f"로컬 파일 {file_name}과 {thumbnail_name}이 삭제되었습니다.")
    except ClientError as e:
        logging.error(f"S3 업로드 중 오류 발생: {e}")
    except Exception as e:
        logging.error(f"예상치 못한 오류 발생: {e}")

def create_thumbnail(video_path, thumbnail_path):
    """비디오에서 썸네일을 생성합니다."""
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(thumbnail_path, frame)
    cap.release()

async def list_s3_videos():
    """
    S3 버킷에 저장된 영상 목록과 썸네일 URL을 반환합니다.
    """
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        
        if 'Contents' not in response:
            return []

        video_list = []
        for obj in response['Contents']:
            file_name = obj['Key']
            if file_name.endswith('.avi'):
                # 파일 이름에서 정보 추출
                parts = file_name.split('_')
                if len(parts) >= 4:
                    person_name = parts[0]
                    emotion = parts[1]
                    date_time = '_'.join(parts[2:4]).replace('.avi', '')
                    
                    # 썸네일 URL 생성
                    thumbnail_name = f"thumbnail_{file_name.replace('.avi', '.jpg')}"
                    thumbnail_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{thumbnail_name}"
                    
                    # 영상 다운로드 URL 생성
                    video_url = s3_client.generate_presigned_url('get_object',
                                                                 Params={'Bucket': BUCKET_NAME,
                                                                         'Key': file_name},
                                                                 ExpiresIn=3600)  # URL 유효 시간 1시간
                    
                    video_info = {
                        'file_name': file_name,
                        'person_name': person_name,
                        'emotion': emotion,
                        'date_time': date_time,
                        'thumbnail_url': thumbnail_url,
                        'video_url': video_url  # 영상 다운로드 URL 추가
                    }
                    video_list.append(video_info)

        return video_list

    except ClientError as e:
        logging.error(f"S3 목록 조회 중 오류 발생: {e}")
        return []
    except Exception as e:
        logging.error(f"예상치 못한 오류 발생: {e}")
        return []