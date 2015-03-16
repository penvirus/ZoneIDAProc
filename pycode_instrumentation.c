#include <Python.h>
#include <dlfcn.h>
#include <stdio.h>

int instrument(const char *command)
{
	void *main_hndl = dlopen(NULL, 0x2);

	//int Py_IsInitialized()
	int (*_Py_IsInitialized)() = (int (*)()) dlsym(main_hndl, "Py_IsInitialized");
	if(_Py_IsInitialized == NULL) {
		printf("dlsym Py_IsInitialized is NULL\n");
		goto error;
	}

	//PyInterpreterState *PyInterpreterState_Head()
	PyInterpreterState *(*_PyInterpreterState_Head)() = (PyInterpreterState* (*)()) dlsym(main_hndl, "PyInterpreterState_Head");
	if(_PyInterpreterState_Head == NULL) {
		printf("dlsym PyInterpreterState_Head is NULL\n");
		goto error;
	}

	//PyGILState_STATE PyGILState_Ensure()
	PyGILState_STATE (*_PyGILState_Ensure)() = (PyGILState_STATE (*)()) dlsym(main_hndl, "PyGILState_Ensure");
	if(_PyGILState_Ensure == NULL) {
		printf("dlsym PyGILState_Ensure is NULL\n");
		goto error;
	}

	//void PyGILState_Release(PyGILState_STATE oldstate)
	void (*_PyGILState_Release)(PyGILState_STATE) = (void (*)(PyGILState_STATE)) dlsym(main_hndl, "PyGILState_Release");
	if(_PyGILState_Release == NULL) {
		printf("dlsym PyGILState_Release is NULL\n");
		goto error;
	}

	//int PyRun_SimpleString(const char *command)
	int (*_PyRun_SimpleString)(const char*) = (int (*)(const char *)) dlsym(main_hndl, "PyRun_SimpleString");
	if(_PyRun_SimpleString == NULL) {
		printf("dlsym PyRun_SimpleString is NULL\n");
		goto error;
	}


	if(!_Py_IsInitialized()){
		printf("Py_IsInitialized returned false.\n");
		goto error;
	}

	PyInterpreterState *head = _PyInterpreterState_Head();
	if(head == NULL) {
		printf("Interpreter is not initialized\n");
		goto error;
	}

	PyGILState_STATE pyGILState = _PyGILState_Ensure();
	_PyRun_SimpleString(command);
	_PyGILState_Release(pyGILState);

	return 1;
error:
	return 0;
}
