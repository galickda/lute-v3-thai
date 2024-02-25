# Lute v3 with chinese support



https://github.com/fanyingfx/lute-v3/assets/57335844/885fdc68-bf08-41dd-8553-b1d45f9aa9b0




This is modified version of [Lute](https://github.com/jzohrab/lute-v3), it supports Chinese, accurately, it's Mandarin.

## Installation and Upgrade

### Installation

At first, you should Install Python and [activate virtual environment](./README_PyPi.md)

After the virtual environment activated, you could use  command

```
pip install https://github.com/fanyingfx/lute-v3/releases/download/3.1.2b1/lute3-3.1.2b1-py3-none-any.whl --upgrade
```
to install the lute supporting Chinese.

And you can check the latest version from repo's page
and replace the link to the latest version link.

### Upgrade



https://github.com/fanyingfx/lute-v3/assets/57335844/ca991279-2643-4256-bbd9-43220979b6ef



## Migration
Because of some big change in the codebase, some features may not add to the lute.
I am also working on adding Chinese support to original lute, but need some time to find a suitable solution to not make a big change in Lute's code.

The database is full compatible with lute's db, but I also recommend you to create a new database to use.

If you want to migrate previous lute to this version, you can copy your previous database and then in this version of lute's Language Setting,
change the Parse as to Mandarin.
![image](https://github.com/fanyingfx/lute-v3/assets/57335844/7ce900cb-fd09-4962-9214-37c45762ae41)



## User Defined Dictionary
Another thing, it supports the user defined Chinese words dictionary to make parsed result more correct.
after start the lute and mark some terms in reading, then in the lute's data folder you can find a file `mandarin.user_dict.txt`.
in the file: 
```
竹条,编 // it means you make the parser always pase "竹条编" as "竹条" and "编", this is for multiple-words terms
珍珠鸟 // it mean parser will parse 珍珠鸟 as one terms
```
You can also add your define terms in the file , only Chinese  with English comma ',' not Chinese's comma '，'



## 
You can reach me by email: `fanyingfx@outlook.com`.
or find me in the Lute Discord @fanyingfx and send me any problem in the *Mandarin parser fork issue?* Thread about the Chinese forked Lute issues.

