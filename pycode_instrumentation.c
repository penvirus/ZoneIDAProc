#include <Python.h>
#include <dlfcn.h>
#include <stdio.h>

static int (*_Py_IsInitialized)() = NULL;
static PyInterpreterState *(*_PyInterpreterState_Head)() = NULL;
static PyGILState_STATE (*_PyGILState_Ensure)() = NULL;
static void (*_PyGILState_Release)(PyGILState_STATE) = NULL;
static int (*_PyRun_SimpleString)(const char *) = NULL;
static int (*_PyRun_SimpleFile)(FILE *, const char *) = NULL;

static int _call_dlsym()
{
	void *main_handle = dlopen(NULL, 0x2);

	//int Py_IsInitialized()
	_Py_IsInitialized = (int (*)()) dlsym(main_handle, "Py_IsInitialized");
	if(_Py_IsInitialized == NULL) {
		printf("dlsym Py_IsInitialized is NULL\n");
		goto error;
	}

	//PyInterpreterState *PyInterpreterState_Head()
	_PyInterpreterState_Head = (PyInterpreterState* (*)()) dlsym(main_handle, "PyInterpreterState_Head");
	if(_PyInterpreterState_Head == NULL) {
		printf("dlsym PyInterpreterState_Head is NULL\n");
		goto error;
	}

	//PyGILState_STATE PyGILState_Ensure()
	_PyGILState_Ensure = (PyGILState_STATE (*)()) dlsym(main_handle, "PyGILState_Ensure");
	if(_PyGILState_Ensure == NULL) {
		printf("dlsym PyGILState_Ensure is NULL\n");
		goto error;
	}

	//void PyGILState_Release(PyGILState_STATE oldstate)
	_PyGILState_Release = (void (*)(PyGILState_STATE)) dlsym(main_handle, "PyGILState_Release");
	if(_PyGILState_Release == NULL) {
		printf("dlsym PyGILState_Release is NULL\n");
		goto error;
	}

	//int PyRun_SimpleString(const char *command)
	_PyRun_SimpleString = (int (*)(const char *)) dlsym(main_handle, "PyRun_SimpleString");
	if(_PyRun_SimpleString == NULL) {
		printf("dlsym PyRun_SimpleString is NULL\n");
		goto error;
	}

	//int PyRun_SimpleFile(FILE *fp, const char *filename)
	_PyRun_SimpleFile = (int (*)(FILE *, const char *)) dlsym(main_handle, "PyRun_SimpleFile");
	if(_PyRun_SimpleFile == NULL) {
		printf("dlsym PyRun_SimpleFile is NULL\n");
		goto error;
	}

	return 1;
error:
	return 0;
}

int instrument_string(const char *command)
{
	if(!_call_dlsym()) {
		printf("_call_dlsym is failed");
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

int instrument_file(const char *filename)
{
	FILE *fp = NULL;

	if(!_call_dlsym()) {
		printf("_call_dlsym is failed");
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
	fp = fopen(filename, "r");
	if(fp == NULL) {
		printf("file %s doesn't exist", filename);
		goto error;
	}
	_PyRun_SimpleFile(fp, "Instrumentation");
	_PyGILState_Release(pyGILState);

	if(fp)
		fclose(fp);
	return 1;
error:
	if(fp)
		fclose(fp);
	return 0;
}
