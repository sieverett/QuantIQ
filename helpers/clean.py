import os
import glob


def clean():
    os.remove('.streamlit/secrets.toml')
    for dir_ in ['bulk_output', 'bulk']:
        files = glob.glob(f'{dir_}/*')
        for f in files:
            os.remove(f)


if __name__ == '__main__':
    clean()
