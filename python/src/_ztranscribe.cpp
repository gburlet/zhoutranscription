#include "transcription.h"
#include "realtime.h"
#include "plugin.h"
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>
#include <boost/numpy.hpp>

#include <iostream>

using Vamp::RealTime;
using namespace std;

namespace py = boost::python;
namespace np = boost::numpy;

typedef vector<float> fVector;
typedef vector<Transcription::Feature> FeatureList;
typedef map<int, FeatureList> FeatureSet;

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
        py::converter::registry::push_back(&convertible, &construct, py::type_id<vector<T> >()); 
    }

    static void* convertible(PyObject* obj_ptr){
        if (!PySequence_Check(obj_ptr)) {
            return 0;
        }
        else {
            return obj_ptr;
        }
    }

    static void construct(PyObject* obj_ptr, py::converter::rvalue_from_python_stage1_data* data){
        // Get pointer to memory where the vector will be constructed
        void* storage = ((py::converter::rvalue_from_python_storage<std::vector<T> >*)(data))->storage.bytes;

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
            v->push_back(py::extract<T>(PySequence_GetItem(obj_ptr, i)));
        }

        // stash the pointer location for boost.python
        data->convertible = storage;
    }
};

void inputAudio(Transcription t, np::ndarray const & npAudio) {
    // check the audio array is of type np.double
    if (npAudio.get_dtype() != np::dtype::get_builtin<double>()) {
        PyErr_SetString(PyExc_TypeError, "Incorrect array data type");
        py::throw_error_already_set();
    }
    
    // check it is a monaural signal
    if (npAudio.get_nd() != 1) {
        PyErr_SetString(PyExc_TypeError, "Incorrect number of dimensions. Should be (1,)");
        py::throw_error_already_set();
    }

    int numSamples = npAudio.shape(0);
    double * audio = reinterpret_cast<double*>(npAudio.get_data());
    t.setAudioData(audio, numSamples);
}

BOOST_PYTHON_MODULE(transcribe)
{
    using namespace boost::python;

    VectorFromList<float>();

    // initialize boost::numpy
    np::initialize();

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
        .def("inputAudio", &inputAudio)
        .def("getRemainingFeatures", &Transcription::getRemainingFeatures)
    ;

    class_<Transcription::Feature>("Feature")
        .def_readwrite("timestamp", &Transcription::Feature::timestamp)
        .def_readwrite("duration", &Transcription::Feature::duration)
        .def_readwrite("values", &Transcription::Feature::values)
    ;

    class_<FeatureList>("FeatureList")
        .def(vector_indexing_suite<FeatureList>())
    ;

    class_<FeatureSet>("FeatureSet")
        .def(map_indexing_suite<FeatureSet>())
    ;
}
