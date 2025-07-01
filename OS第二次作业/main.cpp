#include "Memory.h"

using namespace std;

void start(int xuanxiang)
{
	string algorithm = (xuanxiang == '1' ? string("LRU") : string("FIFO"));


	Memory myMemory;						 //�����ڴ����
	myMemory.Init();					
	srand((unsigned)time(NULL));			//��ȡ���������

	cout << "��ǰ�㷨Ϊ��" << algorithm << "   ��ģ�����Ϊ��" << endl << endl;

	myMemory.Simulate(algorithm);		//���ո��㷨�͸�ִ��ģʽ����ģ��

	cout << "��ǰ�㷨Ϊ��" << algorithm << "  "<<endl;
	cout << "-------------------------" << endl
		<< "��ִ��" << myMemory.getRunTime() << "��" << endl
		<< "ȱҳ����Ϊ" << myMemory.getmissPageTime() << "��" << endl
		<< "ȱҳ��Ϊ" << myMemory.getmissPageRate() << endl
		<< "--------------------------" << endl;
}

int menu()
{
	cout << "�����ҳ���䷽ʽ" << endl << endl;
	cout << "��ѡ���û��㷨��" << endl;
	cout << "1. LRU" << endl;
	cout << "2. FIFO" << endl;
	cout << "0. �˳�" << endl;
	cout << "--------------" << endl;
	cout << "[������1/2/0:]";
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
			cout << "���س�������";
			while (1) {
				if (_getch() == '\r')
					break;
			}
			system("cls");
		}
	}
	return 0;
}