import os
import datetime
from supabase import create_client

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def salvar(dados):
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()

    supabase.table('noticias').upsert(
        {
            'titulo':      dados['titulo'],
            'url':         dados['url'],
            'fonte':       dados['fonte'],
            'corpo':       dados.get('corpo', ''),   # ← novo campo
            'data_coleta': agora
        },
        on_conflict='url'
    ).execute()