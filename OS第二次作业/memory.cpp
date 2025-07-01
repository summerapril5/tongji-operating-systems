#include "Memory.h"

using namespace std;

InstNumber getRand(InstNumber low, InstNumber high)
{
	if (high - low == -1) { return high; }	//若aim是0或OTAL_INSTRUCTIONS-1，则进入该函数可能会使high-low=-1，故作此处理
	return (rand() % (high - low + 1) + low);
}

// 初始化
void Memory::Init()
{
	this->memoryBlocks.resize(MaxBlocks, EMPTY_BLOCK);
	this->instructionExecuted.resize(OTAL_INSTRUCTIONS, false);
	while (!this->LRU_Queue.empty()) { this->LRU_Queue.pop(); }

	this->executionCount = 0;
	this->pageFaultCount = 0;
	this->remainingInstructions = OTAL_INSTRUCTIONS;
}

// 执行一条指令
void Memory::execute(string algorithm, InstNumber aim)
{
	this->executionCount++;		//更新运行次数

	PageNumber page = aim / 10;
	BlockNumber pos = 0;

	bool exist_flag = false;      //标记该页是否在内存中
	bool empty_flag = false;   //标记缺页情况下是否需要页面调配
	PageNumber old = -1;

	cout << "第" << setw(4) << executionCount << "次：|";
	for (pos = 0; pos < MaxBlocks; ++pos)
	{
		cout << pos << ":";
		if (memoryBlocks[pos] == EMPTY_BLOCK)
			cout << "空";
		else
			cout << setw(2) << memoryBlocks[pos];

		cout << "|";
	}
	cout << " 选中第" << setw(3) << aim << "条指令,";
	cout << "物理地址为" << setw(3) << aim << "位于" << setw(2) << page << "页" << aim % 10 << "号指令。";

	//检测该页是否已经在内存中 
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
		//检测内存中有无空闲块 
		for (pos = 0; pos < MaxBlocks; ++pos)
		{
			if (memoryBlocks[pos] == EMPTY_BLOCK)
			{
				memoryBlocks[pos] = page;
				empty_flag = true;
				if (algorithm == string("LRU"))
				{
					LRU_Queue.push(pos);//将其压入最近最少使用队列
				}
				break;
			}
		}
		//所有内存块均满，需要进行调页
		if (!empty_flag) {
			//进行调页
			old = adjust(algorithm, pos);
			memoryBlocks[pos] = page;
		}
	}

	if (!exist_flag) {
		cout << "缺页";
		if (empty_flag)
			cout << " 内存块" << pos << "为空，将第" << page << "号页放在其中，";
		else
			cout << " 将内存块" << pos << "中原有的第" << old << "号页调出, 将第" << page << "号页调入，";
		cout << "执行该指令";
	}
	else
		cout << "直接执行该指令"<<endl;

	cout << endl << endl;
}

// 模拟分区调页过程 
void Memory::Simulate(string algorithm)
{
	InstNumber aim;
	//随机选取一个起始指令
	aim = getRand(0, OTAL_INSTRUCTIONS - 1);
	execute(algorithm, aim);
	remainingInstructions--; instructionExecuted[aim] = true;
	//顺序执行下一条指令
	aim++;
	execute(algorithm, aim);
	remainingInstructions--; instructionExecuted[aim] = true;

	while (true)
	{
		if (!remainingInstructions)
			break;

		//跳转到前地址部分
		aim = getRand(0, aim - 1);
		if (aim != OTAL_INSTRUCTIONS && instructionExecuted[aim] == false) {
			remainingInstructions--;
			instructionExecuted[aim] = true;
			execute(algorithm, aim);
		}

		if (!remainingInstructions)
			break;

		//顺序执行下一条指令
		aim++;
		if (aim != OTAL_INSTRUCTIONS && instructionExecuted[aim] == false) {
			remainingInstructions--;
			instructionExecuted[aim] = true;
			execute(algorithm, aim);
		}

		if (!remainingInstructions)
			break;

		//跳转到后地址部分
		aim = getRand(aim + 1, OTAL_INSTRUCTIONS - 1);
		if (aim != OTAL_INSTRUCTIONS && instructionExecuted[aim] == false) {
			remainingInstructions--;
			instructionExecuted[aim] = true;
			execute(algorithm, aim);
		}

		if (!remainingInstructions)
			break;

		//顺序执行下一条指令
		aim++;
		if (aim != OTAL_INSTRUCTIONS && instructionExecuted[aim] == false) {
			remainingInstructions--;
			instructionExecuted[aim] = true;
			execute(algorithm, aim);
		}
	}
}


// 页面置换
PageNumber Memory::adjust(string algorithm, BlockNumber& pos)
{
	PageNumber old;
	if (algorithm == "FIFO")
	{
		pos = (this->pageFaultCount - 1) % 4;	//缺页次数为1, 则将0号内存的页调出, 将当前指令调入0 号内存中...以此类推
		old = memoryBlocks[pos];
	}
	else if (algorithm == "LRU")
	{
		pos = LRU_Queue.front();		//取队列头元素 => 最近最少使用的页面
		LRU_Queue.pop();
		LRU_Queue.push(pos);			//将其压入队尾

		old = memoryBlocks[pos];
	}

	return old;
}

