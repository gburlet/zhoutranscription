#include "transcription.h"
#include <boost/python.hpp>

BOOST_PYTHON_MODULE(transcribe)
{
    using namespace boost::python;

    class_<Transcription>("Transcription", init<float>())
    ;
}
