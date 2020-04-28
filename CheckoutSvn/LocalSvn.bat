net use Z: \\TPCNDC04\Mirror
echo off 
Z:

cd /d z:/TempSVN\RepoGondor\svn

echo Unlock Local SVN
"Z:\TempSVN\RepoGondor\svn\bin\svn" propdel svn:sync-lock --revprop -r 0 file:///Z:/TempSVN/RepoGondor/svn/svn-psgfw-platform14
"Z:\TempSVN\RepoGondor\svn\bin\svn" propdel svn:sync-lock --revprop -r 0 file:///Z:/TempSVN/RepoGondor/svn/svn-psgfw-core

echo Syn Local with SVN server
REM "Z:\TempSVN\RepoGondor\svn\bin\svnsync.exe" sync file:///Z:/TempSVN/RepoGondor/svn/svn-psgfw-platform14
REM "Z:\TempSVN\RepoGondor\svn\bin\svnsync.exe" sync file:///Z:/TempSVN/RepoGondor/svn/svn-psgfw-core


echo off
echo Checkout your project from svn://localhost/svn/svn-psgfw-platform14/
echo (Do not use file:///Z:/TempSVN/RepoGondor/svn/svn-psgfw-platform14, otherwise, external folder can't be checkout)
echo Username: svn
echo Password: svn
echo on

"Z:\TempSVN\RepoGondor\svn\bin\svnserve" --daemon --root Z:\TempSVN\RepoGondor
