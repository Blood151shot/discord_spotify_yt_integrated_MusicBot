from fastapi import FastAPI, HTTPException

from spotify_auth import create_oauth
from database_manager import save_user


app = FastAPI()


@app.get("/callback")
def callback(
    code: str,
    state: str
):

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Spotify authorization code is missing"
        )

    if not state:
        raise HTTPException(
            status_code=400,
            detail="Discord user ID is missing"
        )

    try:

        oauth = create_oauth()

        token_info = oauth.get_access_token(
            code=code,
            check_cache=False
        )

        refresh_token = token_info.get(
            "refresh_token"
        )

        if not refresh_token:
            raise HTTPException(
                status_code=400,
                detail="Spotify did not return a refresh token"
            )

        save_user(
            discord_id=state,
            refresh_token=refresh_token
        )

        return {
            "message":
            "Spotify connected successfully 🎧 You can close this page"
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"Spotify callback error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Spotify authentication failed"
        )