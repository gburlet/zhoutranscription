#include "transcription.h"
#include "realtime.h"
#include "plugin.h"
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

using Vamp::RealTime;

using namespace boost::python;
using namespace std;

typedef vector<float> fVector;

string fVec_print(fVector x) {
    stringstream res;
    res << "[";
    for(fVector::iterator iter = x.begin(); iter != x.end(); ++iter) {
        if (iter != x.begin()) {
            res << ", ";
        }
        res << *iter;
    }
    res << "]";

    return res.str();
}

/*
 * Converter for python lists to vector<T>
 */
template<typename T>
struct VectorFromList {
    VectorFromList() { 
        converter::registry::push_back(&convertible, &construct, type_id<vector<T> >()); 
    }

    static void* convertible(PyObject* obj_ptr){
        if (!PySequence_Check(obj_ptr)) {
            return 0;
        }
        else {
            return obj_ptr;
        }
    }

    static void construct(PyObject* obj_ptr, converter::rvalue_from_python_stage1_data* data){
        // Get pointer to memory where the vector will be constructed
        void* storage = ((converter::rvalue_from_python_storage<std::vector<T> >*)(data))->storage.bytes;

        // construct the new vector in place using the python list data
        new (storage) vector<T>();
        vector<T> *v = (vector<T>*)(storage);
        long len = PySequence_Size(obj_ptr); 
        if (len < 0) {
            abort();
        }

        v->reserve(len); 
        
        // fill the C++ vector from the Python list data
        for(int i = 0; i < len; i++) { 
            v->push_back(extract<T>(PySequence_GetItem(obj_ptr, i)));
        }

        // stash the pointer location for boost.python
        data->convertible = storage;
    }
};

BOOST_PYTHON_MODULE(transcribe)
{
    VectorFromList<float>();

    class_<fVector>("fVec")
        .def(vector_indexing_suite<fVector>())
        .def("__str__", &fVec_print)
        .def("__repr__", &fVec_print)
    ;
    
    class_<RealTime>("RealTime", init<int,int>())
        .def("fromSeconds", static_cast<RealTime(*)(double)>(&RealTime::fromSeconds))
        .staticmethod("fromSeconds")
        .def("fromMilliseconds", static_cast<RealTime(*)(int)>(&RealTime::fromMilliseconds))
        .staticmethod("fromMilliseconds")
        .def_readwrite("sec", &RealTime::sec)
        .def_readwrite("nsec", &RealTime::nsec)
    ;

    class_<Transcription>("Transcription", init<float>())
        .def("initialise", &Transcription::initialise)
        .def("reset", &Transcription::reset)
        .def("process", &Transcription::process)
        .def("getRemainingFeatures", &Transcription::getRemainingFeatures)
    ;

    class_<Transcription::Feature>("Feature")
        .def_readwrite("timestamp", &Transcription::Feature::timestamp)
        .def_readwrite("duration", &Transcription::Feature::duration)
        .def_readwrite("values", &Transcription::Feature::values)
    ;
}
