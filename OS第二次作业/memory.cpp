#include "Memory.h"

using namespace std;

InstNumber getRand(InstNumber low, InstNumber high)
{
	if (high - low == -1) { return high; }	//��aim��0��OTAL_INSTRUCTIONS-1�������ú������ܻ�ʹhigh-low=-1�������˴���
	return (rand() % (high - low + 1) + low);
}

// ��ʼ��
void Memory::Init()
{
	this->memoryBlocks.resize(MaxBlocks, EMPTY_BLOCK);
	this->instructionExecuted.resize(OTAL_INSTRUCTIONS, false);
	while (!this->LRU_Queue.empty()) { this->LRU_Queue.pop(); }

	this->executionCount = 0;
	this->pageFaultCount = 0;
	this->remainingInstructions = OTAL_INSTRUCTIONS;
}

// ִ��һ��ָ��
void Memory::execute(string algorithm, InstNumber aim)
{
	this->executionCount++;		//�������д���

	PageNumber page = aim / 10;
	BlockNumber pos = 0;

	bool exist_flag = false;      //��Ǹ�ҳ�Ƿ����ڴ���
	bool empty_flag = false;   //���ȱҳ������Ƿ���Ҫҳ�����
	PageNumber old = -1;

	cout << "��" << setw(4) << executionCount << "�Σ�|";
	for (pos = 0; pos < MaxBlocks; ++pos)
	{
		cout << pos << ":";
		if (memoryBlocks[pos] == EMPTY_BLOCK)
			cout << "��";
		else
			cout << setw(2) << memoryBlocks[pos];

		cout << "|";
	}
	cout << " ѡ�е�" << setw(3) << aim << "��ָ��,";
	cout << "�����ַΪ" << setw(3) << aim << "λ��" << setw(2) << page << "ҳ" << aim % 10 << "��ָ�";

	//����ҳ�Ƿ��Ѿ����ڴ��� 
	for (pos = 0; pos < MaxBlocks; ++pos)
	{
		if (memoryBlocks[pos] == page)
		{
			exist_flag = true;
		}
	}

	if (!exist_flag) {
		this->pageFaultCount++;		

		empty_flag = false;
		//����ڴ������޿��п� 
		for (pos = 0; pos < MaxBlocks; ++pos)
		{
			if (memoryBlocks[pos] == EMPTY_BLOCK)
			{
				memoryBlocks[pos] = page;
				empty_flag = true;
				if (algorithm == string("LRU"))
				{
					LRU_Queue.push(pos);//����ѹ���������ʹ�ö���
				}
				break;
			}
		}
		//�����ڴ���������Ҫ���е�ҳ
		if (!empty_flag) {
			//���е�ҳ
			old = adjust(algorithm, pos);
			memoryBlocks[pos] = page;
		}
	}

	if (!exist_flag) {
		cout << "ȱҳ";
		if (empty_flag)
			cout << " �ڴ��" << pos << "Ϊ�գ�����" << page << "��ҳ�������У�";
		else
			cout << " ���ڴ��" << pos << "��ԭ�еĵ�" << old << "��ҳ����, ����" << page << "��ҳ���룬";
		cout << "ִ�и�ָ��";
	}
	else
		cout << "ֱ��ִ�и�ָ��"<<endl;

	cout << endl << endl;
}

// ģ�������ҳ���� 
void Memory::Simulate(string algorithm)
{
	InstNumber aim;
	//���ѡȡһ����ʼָ��
	aim = getRand(0, OTAL_INSTRUCTIONS - 1);
	execute(algorithm, aim);
	remainingInstructions--; instructionExecuted[aim] = true;
	//˳��ִ����һ��ָ��
	aim++;
	execute(algorithm, aim);
	remainingInstructions--; instructionExecuted[aim] = true;

	while (true)
	{
		if (!remainingInstructions)
			break;

		//��ת��ǰ��ַ����
		aim = getRand(0, aim - 1);
		if (aim != OTAL_INSTRUCTIONS && instructionExecuted[aim] == false) {
			remainingInstructions--;
			instructionExecuted[aim] = true;
			execute(algorithm, aim);
		}

		if (!remainingInstructions)
			break;

		//˳��ִ����һ��ָ��
		aim++;
		if (aim != OTAL_INSTRUCTIONS && instructionExecuted[aim] == false) {
			remainingInstructions--;
			instructionExecuted[aim] = true;
			execute(algorithm, aim);
		}

		if (!remainingInstructions)
			break;

		//��ת�����ַ����
		aim = getRand(aim + 1, OTAL_INSTRUCTIONS - 1);
		if (aim != OTAL_INSTRUCTIONS && instructionExecuted[aim] == false) {
			remainingInstructions--;
			instructionExecuted[aim] = true;
			execute(algorithm, aim);
		}

		if (!remainingInstructions)
			break;

		//˳��ִ����һ��ָ��
		aim++;
		if (aim != OTAL_INSTRUCTIONS && instructionExecuted[aim] == false) {
			remainingInstructions--;
			instructionExecuted[aim] = true;
			execute(algorithm, aim);
		}
	}
}


// ҳ���û�
PageNumber Memory::adjust(string algorithm, BlockNumber& pos)
{
	PageNumber old;
	if (algorithm == "FIFO")
	{
		pos = (this->pageFaultCount - 1) % 4;	//ȱҳ����Ϊ1, ��0���ڴ��ҳ����, ����ǰָ�����0 ���ڴ���...�Դ�����
		old = memoryBlocks[pos];
	}
	else if (algorithm == "LRU")
	{
		pos = LRU_Queue.front();		//ȡ����ͷԪ�� => �������ʹ�õ�ҳ��
		LRU_Queue.pop();
		LRU_Queue.push(pos);			//����ѹ���β

		old = memoryBlocks[pos];
	}

	return old;
}

