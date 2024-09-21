import boto3
import logging
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

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
    지정된 파일을 S3 버킷에 업로드합니다.
    """
    try:
        s3_client.upload_file(file_name, BUCKET_NAME, file_name)
        logging.info(f"파일 {file_name}이 S3 버킷 {BUCKET_NAME}에 성공적으로 업로드되었습니다.")
        
        # 로컬 파일 삭제
        os.remove(file_name)
        logging.info(f"로컬 파일 {file_name}이 삭제되었습니다.")
    except ClientError as e:
        logging.error(f"S3 업로드 중 오류 발생: {e}")
    except Exception as e:
        logging.error(f"예상치 못한 오류 발생: {e}")

async def list_s3_videos():
    """
    S3 버킷��� 저장된 영상 목록을 반환합니다.
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
                    
                    video_info = {
                        'file_name': file_name,
                        'person_name': person_name,
                        'emotion': emotion,
                        'date_time': date_time
                    }
                    video_list.append(video_info)

        return video_list

    except ClientError as e:
        logging.error(f"S3 목록 조회 중 오류 발생: {e}")
        return []
    except Exception as e:
        logging.error(f"예상치 못한 오류 발생: {e}")
        return []