#include "Memory.h"

using namespace std;

void start(int xuanxiang)
{
	string algorithm = (xuanxiang == '1' ? string("LRU") : string("FIFO"));


	Memory myMemory;						 //创建内存对象
	myMemory.Init();					
	srand((unsigned)time(NULL));			//获取随机数种子

	cout << "当前算法为：" << algorithm << "   其模拟过程为：" << endl << endl;

	myMemory.Simulate(algorithm);		//按照该算法和该执行模式进行模拟

	cout << "当前算法为：" << algorithm << "  "<<endl;
	cout << "-------------------------" << endl
		<< "共执行" << myMemory.getRunTime() << "次" << endl
		<< "缺页次数为" << myMemory.getmissPageTime() << "次" << endl
		<< "缺页率为" << myMemory.getmissPageRate() << endl
		<< "--------------------------" << endl;
}

int menu()
{
	cout << "请求分页分配方式" << endl << endl;
	cout << "请选择置换算法：" << endl;
	cout << "1. LRU" << endl;
	cout << "2. FIFO" << endl;
	cout << "0. 退出" << endl;
	cout << "--------------" << endl;
	cout << "[请输入1/2/0:]";
	int i;
	while (1) {
		i = _getch();
		if (i >= '0' && i <= '2') {
			cout << i - '0';
			break;
		}
	}
	cout << endl;
	cout << endl;
	return i;
}

int main()
{
	int xuanxiang;

	while (1) {
		xuanxiang = menu();
		if (xuanxiang == '0')
			break;
		else {
			system("cls");
			start(xuanxiang);
			cout << endl;
			cout << "按回车键继续";
			while (1) {
				if (_getch() == '\r')
					break;
			}
			system("cls");
		}
	}
	return 0;
}