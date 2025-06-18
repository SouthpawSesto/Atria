echo off
echo Entering venv

call .venv\Scripts\activate.bat

echo Build Init...

call nuitka AtriaApplication.py ^
    --standalone ^
    --windows-console-mode=force^
    --windows-icon-from-ico=Art\AtriaLogo2.ico^
    --verbose ^
    --show-progress ^
    --show-modules^
    --show-scons^
    --include-module=modelEditWindow^
    --include-package=transformers.models^
    --include-data-dir=.venv\Lib\site-packages\transformers\models=transformers\models^
    --include-distribution-metadata=torchaudio^
    --enable-plugin=tk-inter^
    --nofollow-import-to=transformers.models.nllb^
    --nofollow-import-to=transformers.models.mbart50^
    --nofollow-import-to=transformers.models.cpm^
    --nofollow-import-to=transformers.models.code_llama^
    --nofollow-import-to=transformers.models.barthez^
    --nofollow-import-to=transformers.models.mluke^
    --nofollow-import-to=transformers.models.gpt_sw3^
    --nofollow-import-to=transformers.models.bartpho^
    --nofollow-import-to=transformers.models.dinov2_with_registers^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/nllb=transformers/models/nllb"^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/mbart50=transformers/models/mbart50"^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/cpm=transformers/models/cpm"^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/code_llama=transformers/models/code_llama"^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/barthez=transformers/models/barthez"^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/mluke=transformers/models/mluke"^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/gpt_sw3=transformers/models/gpt_sw3"^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/bartpho=transformers/models/bartpho"^
    --include-data-dir=".venv/Lib/site-packages/transformers/models/dinov2_with_registers=transformers/models/dinov2_with_registers"^

echo Sending Notification...

call python notification.py

echo Build Complete
