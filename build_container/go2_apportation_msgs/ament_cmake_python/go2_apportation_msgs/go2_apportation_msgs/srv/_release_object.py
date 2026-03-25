# generated from rosidl_generator_py/resource/_idl.py.em
# with input from go2_apportation_msgs:srv/ReleaseObject.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ReleaseObject_Request(type):
    """Metaclass of message 'ReleaseObject_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'OPEN_GRIPPER': 0,
        'DROP_SAFE': 1,
        'HANDOVER_RELEASE': 2,
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('go2_apportation_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'go2_apportation_msgs.srv.ReleaseObject_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__release_object__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__release_object__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__release_object__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__release_object__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__release_object__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'OPEN_GRIPPER': cls.__constants['OPEN_GRIPPER'],
            'DROP_SAFE': cls.__constants['DROP_SAFE'],
            'HANDOVER_RELEASE': cls.__constants['HANDOVER_RELEASE'],
        }

    @property
    def OPEN_GRIPPER(self):
        """Message constant 'OPEN_GRIPPER'."""
        return Metaclass_ReleaseObject_Request.__constants['OPEN_GRIPPER']

    @property
    def DROP_SAFE(self):
        """Message constant 'DROP_SAFE'."""
        return Metaclass_ReleaseObject_Request.__constants['DROP_SAFE']

    @property
    def HANDOVER_RELEASE(self):
        """Message constant 'HANDOVER_RELEASE'."""
        return Metaclass_ReleaseObject_Request.__constants['HANDOVER_RELEASE']


class ReleaseObject_Request(metaclass=Metaclass_ReleaseObject_Request):
    """
    Message class 'ReleaseObject_Request'.

    Constants:
      OPEN_GRIPPER
      DROP_SAFE
      HANDOVER_RELEASE
    """

    __slots__ = [
        '_release_mode',
        '_verify_open',
    ]

    _fields_and_field_types = {
        'release_mode': 'uint8',
        'verify_open': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.release_mode = kwargs.get('release_mode', int())
        self.verify_open = kwargs.get('verify_open', bool())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.release_mode != other.release_mode:
            return False
        if self.verify_open != other.verify_open:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def release_mode(self):
        """Message field 'release_mode'."""
        return self._release_mode

    @release_mode.setter
    def release_mode(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'release_mode' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'release_mode' field must be an unsigned integer in [0, 255]"
        self._release_mode = value

    @builtins.property
    def verify_open(self):
        """Message field 'verify_open'."""
        return self._verify_open

    @verify_open.setter
    def verify_open(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'verify_open' field must be of type 'bool'"
        self._verify_open = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_ReleaseObject_Response(type):
    """Metaclass of message 'ReleaseObject_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('go2_apportation_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'go2_apportation_msgs.srv.ReleaseObject_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__release_object__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__release_object__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__release_object__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__release_object__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__release_object__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ReleaseObject_Response(metaclass=Metaclass_ReleaseObject_Response):
    """Message class 'ReleaseObject_Response'."""

    __slots__ = [
        '_success',
        '_result_code',
        '_message',
    ]

    _fields_and_field_types = {
        'success': 'boolean',
        'result_code': 'uint16',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', bool())
        self.result_code = kwargs.get('result_code', int())
        self.message = kwargs.get('message', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.success != other.success:
            return False
        if self.result_code != other.result_code:
            return False
        if self.message != other.message:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'success' field must be of type 'bool'"
        self._success = value

    @builtins.property
    def result_code(self):
        """Message field 'result_code'."""
        return self._result_code

    @result_code.setter
    def result_code(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'result_code' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'result_code' field must be an unsigned integer in [0, 65535]"
        self._result_code = value

    @builtins.property
    def message(self):
        """Message field 'message'."""
        return self._message

    @message.setter
    def message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'message' field must be of type 'str'"
        self._message = value


class Metaclass_ReleaseObject(type):
    """Metaclass of service 'ReleaseObject'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('go2_apportation_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'go2_apportation_msgs.srv.ReleaseObject')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__release_object

            from go2_apportation_msgs.srv import _release_object
            if _release_object.Metaclass_ReleaseObject_Request._TYPE_SUPPORT is None:
                _release_object.Metaclass_ReleaseObject_Request.__import_type_support__()
            if _release_object.Metaclass_ReleaseObject_Response._TYPE_SUPPORT is None:
                _release_object.Metaclass_ReleaseObject_Response.__import_type_support__()


class ReleaseObject(metaclass=Metaclass_ReleaseObject):
    from go2_apportation_msgs.srv._release_object import ReleaseObject_Request as Request
    from go2_apportation_msgs.srv._release_object import ReleaseObject_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
