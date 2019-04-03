MATRIX CHAT CLIENT
==================
Using matrix-python-sdk and curses (becuse we all love curses)
-------------------------------------------------------------
This is a really simple python chat client. Just for simple use but also to mess-a-round with matrix.
 
INSTALLING ON DEBIAN STRETCH
-----------------------------
Install these dependencies
[olm library](https://git.matrix.org/git/olm/about/)
[matrix-python-sdk-e2e](https://github.com/Zil0/matrix-python-sdk/tree/e2e_beta_2)
can be installed like this 
```
sudo pip3 install -e 'git+https://github.com/Zil0/matrix-python-sdk@e2e_beta_2#egg=matrix-python-sdk-e2e[e2e]' --process-dependency-links
```
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

