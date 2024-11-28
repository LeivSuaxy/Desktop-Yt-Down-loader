import yt_dlp as youtube_dl

async def obtener_formatos(url: str) -> None:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            print("\nFormatos disponibles:")
            print("ID  |  Extensión  |  Resolución  |  Tamaño  |  Tipo")
            print("-" * 60)
            
            for f in info['formats']:
                filesize = f.get('filesize', 'N/A')
                if filesize != 'N/A':
                    filesize = f"{filesize/1024/1024:.1f}MB"
                print(f"{f.get('format_id', 'N/A'):4} | {f.get('ext', 'N/A'):10} | "
                      f"{f.get('resolution', 'N/A'):11} | {filesize:8} | {f.get('format_note', 'N/A')}")
        except Exception as e:
            print(f"Error al obtener formatos: {str(e)}")

async def descargar_video(url: str, format_id: str) -> None:
    ydl_opts = {
        'format': format_id,
        'outtmpl': '%(title)s.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Uso principal
url = input('URL: ')
obtener_formatos(url)
formato_elegido = input('\nIngresa el ID del formato que deseas descargar: ')
descargar_video(url, formato_elegido)