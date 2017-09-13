def cache(cache_var):
    """ This is a semi-confusing decorator saving function for caching variables.
        Usage:
            @cache("__thing")
            def thing(self):
                # Do code to get the result for "thing"
                return result # the result of the function that you want cached

        This means that cache will AUTOMATICALLY check if self.__thing exists, and if not, it will run get_thing()
        and save it into self.__thing. Next time thing() is called, it won't have to run get_thing again, since self.__thing
        already exists. Thus it automatically caches known values.

        :param func_str: A string representation of a getter function from within the class that returns a
                        value to be cached. So if class A has attribute get_thing(), this argument would be "get_thing"
        :param cache_var: A string representation of the variable within which to cache the value received from func_str()
                        For example, if class A wants to save the results from get_thing(), then cache_var might be
                        "__thing", and will be saved under self.__thing
    """
    def _custom_cacher(func_to_wrap):
        # Wrap func_to_wrap with a function that will get, save, and return the value (or return previously saved value)
        def wrapper(self):
            if not hasattr(self, cache_var):
                setattr(self, cache_var, func_to_wrap(self))
            return getattr(self, cache_var)

        return wrapper
    return _custom_cacher