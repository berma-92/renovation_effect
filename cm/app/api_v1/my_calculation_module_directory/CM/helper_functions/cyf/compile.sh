rm -r /tmp/cyf
mkdir /tmp/cyf
cp -r * /tmp/cyf/
cd /tmp/cyf

python compile_cython_files.py build_ext --inplace

cd -

cp -r /tmp/cyf/* .

