MATRIX CHAT CLIENT
==================
Using matrix-python-sdk and curses (becuse we all love curses)
-------------------------------------------------------------
This is a really simple matrix chat client. Just for simple use but also to mess-a-round with matrix. You can drop into the python intrepeter in the middle of a chat and poke around with matrix-sdk :)

Some commands 
```
/join #room:server.net:8448
/code | gets you right into python intrepeter and try funny stuff with matrix for example (ctrl + D to go back to chatting)
/resync need to do this if connection drops for a longer time
/listrooms
``` 

INSTALLING ON DEBIAN STRETCH
-----------------------------
Install dependencies
[olm library](https://git.matrix.org/git/olm/about/)
```
git clone https://git.matrix.org/git/olm/
cd olm
make
sudo make install
sudo ldconfig
```

[matrix-python-sdk-e2e](https://github.com/Zil0/matrix-python-sdk/tree/e2e_beta_2)
```
sudo install python3-dev python3-pip build-essential
pip3 install -e 'git+https://github.com/Zil0/matrix-python-sdk@e2e_beta_2#egg=matrix-python-sdk-e2e[e2e]' --process-dependency-links
```
if it throws segmentation fault do this:

you need to have older pip (dependency-links is not supported in new pip), something like pip 18.1 works, if you have newer you need to do 
```
sudo pip3 install pip==18.1
```
then
```
git clone https://github.com/rbckman/matrixchat.git
```
I also had to do this after I built olm and olm-python
```
sudo ldconfig 
```

