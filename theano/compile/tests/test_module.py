import unittest
from theano.compile.module import *
import theano.tensor as T
import sys

class T_test_module(unittest.TestCase):

    def test_whats_up_with_submembers(self):
        class Blah(FancyModule):
            def __init__(self, stepsize):
                super(Blah, self).__init__(self)
                self.stepsize = Member(T.value(stepsize))
                x = T.dscalar()
            
                self.step = Method([x], x - self.stepsize)

        B = Blah(0.0)
        b = B.make(mode='FAST_RUN')
        b.step(1.0)
        assert b.stepsize == 0.0


    def test_no_shared_members(self):
        """Test that a Result cannot become a Member of two connected Modules
        Fred: What is the purpose of this test? Why we should not be able to do it? I think we should be able to share member.
              Right now it seem to work when it should not.
        """
        x=T.dscalar()
        y=Member(T.dscalar())
        m1=Module()
        m2=Module()
        m1.x=x
        m2.x=x
        m1.y=y
        m2.y=y
        m2.m1=m1
        inst1=m1.make()
        inst2=m2.make()

#        inst1.y=1
#        inst2.y=2
        print inst1
        print inst2
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED1"

    def test_members_in_list_tuple_or_dict(self):
        """Test that a Member which is only included via a list, tuple or dictionary is still treated as if it
        were a toplevel attribute
        Fred: toplevel attribute? do you mean as a toplevel member? m1.x=x work as m1.lx=[x]?
        Fred: why list,tuple of result are casted to member?
        Fred: why no wrapper for dict? Should I add one?
        Fred: why we don't promote a Result to a member, but we do it for lsit and tuple of results?
        """

        def local_test(x,y):
            m1=Module()
            m1.lx=[x]#cast Result]
            m1.ly=[y]
            m1.dx={"x":x}
            m1.dy={"y":y}
            m1.tx=(x,)
            m1.ty=(y,)
            m1.x=x
            m1.y=y
            inst=m1.make()
            assert inst.lx
            assert inst.ly
            assert inst.tx
            assert inst.ty
            inst.y # we don't assert just make the look up as with T.dscalar it return None
            # but it don't return None for value and constant
            self.assertRaises(AttributeError, inst.__getattr__, "x")
            self.assertRaises(AttributeError, inst.__getattr__, "dx")
            self.assertRaises(AttributeError, inst.__getattr__, "dy")

        local_test(T.dscalar(),Member(T.dscalar()))
        local_test(T.value(1),Member(T.value(2)))
        local_test(T.constant(1),Member(T.constant(2)))
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED2"
        
    def test_method_in_list_or_dict(self):
        """Test that a Method which is only included via a list or dictionary is still treated as if it
        were a toplevel attribute
        Fred: why do we promote a list or tuple of fct of result to a Method?
        Fred: why we don't do this of direct fct of results or dict?
        """
        def local_test(x,y):
            m1=Module()
            m1.lx=[x]#cast Result to Member
            m1.ly=[y]#cast Result to Member
            m1.dx={"x":x}
            m1.dy={"y":y}
            m1.tx=(x,)#cast Result to Member
            m1.ty=(y,)#cast Result to Member
            m1.x=x
            m1.y=y

            z=x*2
#            print type(z)
            m1.z=z 
            m1.lz=[z]
            m1.dz={"z":z}
            m1.tz=(z,)
            m1.zz1=Method(x,x*2)
            m1.zz2=m1.zz1
            m1.lzz1=[Method(x,x*2)]
            m1.lzz2=[m1.zz1]
            m1.dzz1={"z":m1.zz1}
            m1.dzz2={"z":Method(x,x*2)}
            m1.tzz1=(Method(x,x*2),)
            m1.tzz2=(m1.zz1,)
            inst=m1.make()

            assert inst.lx
            assert inst.ly
            assert inst.tx
            assert inst.ty
            inst.y # we don't assert just make the look up as with T.dscalar it return None
            # but it don't return None for value and constant
            self.assertRaises(AttributeError, inst.__getattr__, "x")
            self.assertRaises(AttributeError, inst.__getattr__, "dx")
            self.assertRaises(AttributeError, inst.__getattr__, "dy")
            self.assertRaises(AttributeError, inst.__getattr__, "z")
            self.assertRaises(AttributeError, inst.__getattr__, "lz")
            self.assertRaises(AttributeError, inst.__getattr__, "dz")
            self.assertRaises(AttributeError, inst.__getattr__, "tz")
            self.assertRaises(AttributeError, inst.__getattr__, "dzz1")
            self.assertRaises(AttributeError, inst.__getattr__, "dzz2")
            print m1
            print inst
            assert inst.zz1(2)
            assert inst.zz2(2)
            assert inst.lzz1[0](2)
            assert inst.lzz2[0](2)
            assert inst.tzz1[0](2)
            assert inst.tzz2[0](2)

        local_test(T.dscalar(),Member(T.dscalar()))
        local_test(T.value(1),Member(T.value(2)))
        local_test(T.constant(1),Member(T.constant(2)))

        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED3"

    def test_shared_members(self):
        """Test that under a variety of tricky conditions, the shared-ness of Results and Members
        is respected."""

        m1=Module()
        m2=Module()
        x=T.dscalar()
        m1.x=Member(x)
        m2.x=Member(x)
        m1.lx=[Member(x)]
        m2.lx=[Member(x)]
        m1.llx=[[Member(x)],[Member(x)]]
        m2.llx=[[Member(x)],[Member(x)]]
        m1.ltx=[(Member(x),)]
        m2.ltx=[(Member(x),)]
        m1.tx=(Member(x),)
        m2.tx=(Member(x),)
        m1.tlx=([Member(x)],)
        m2.tlx=([Member(x)],)

        #m1.x and m2.x should not be shared as their is no hierarchi link between them.
        inst1=m1.make()
        inst2=m2.make()
        inst1.x=1
        inst2.x=2
        assert inst1.x==1
        assert inst2.x==2
        assert inst1.lx[0]==1
        assert inst2.lx[0]==2
        assert inst1.ltx[0][0]==1#BUG: list of tuple don't work
        assert inst2.ltx[0][0]==2#BUG: list of tuple don't work
        assert inst1.llx[0][0]==1#BUG: list of list don't work
        assert inst2.llx[0][0]==2#BUG: list of list don't work
        assert inst1.llx[1][0]==1#BUG: list of list don't work
        assert inst2.llx[1][0]==2#BUG: list of list don't work
        assert inst1.tx[0]==1
        assert inst2.tx[0]==2
        assert inst1.tlx[0][0]==1#BUG: tuple of list don't work
        assert inst2.tlx[0][0]==2#BUG: tuple of list don't work

        #m1.x and m2.x should be shared as their is a hierarchi link between them.
        m1.m2=m2
        inst=m1.make()
        inst.x=1
        assert inst.x==1
        assert inst.m2.x==1
        assert inst.lx[0]==1
        assert inst.m2.lx[0]==1
        assert inst.tx[0]==1
        assert inst.m2.tx[0]==1
        inst.m2.x=2
        assert inst.x==2
        assert inst.m2.x==2
        assert inst.lx[0]==2
        assert inst.m2.lx[0]==2
        assert inst.tx[0]==2
        assert inst.m2.tx[0]==2

        #same preceding test with list, tuple and dict

        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED4"

    #put them in subModules, sub-sub-Modules, shared between a list and a dict, shared between
    #a list and a submodule with a dictionary, etc...

    def test_shared_members_N(self):
        """Test that Members can be shared an arbitrary number of times between many submodules and
        internal data structures."""
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"

    #put them in subModules, sub-sub-Modules, shared between a list and a dict, shared between
    #a list and a submodule with a dictionary, etc...

    def test_shared_method(self):
        """Test that under a variety of tricky conditions, the shared-ness of Results and Methods
        is respected."""

        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"
    #put them in subModules, sub-sub-Modules, shared between a list and a dict, shared between
    #a list and a submodule with a dictionary, etc...

    def test_shared_method_N(self):
        """Test that Methods can be shared an arbitrary number of times between many submodules and
        internal data structures."""
        
    #put them in subModules, sub-sub-Modules, shared between a list and a dict, shared between
    #a list and a submodule with a dictionary, etc...
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"

    def test_member_method_inputs(self):
        """Test that module Members can be named as Method inputs, in which case the function will
        *not* use the storage allocated for the Module's version of that Member."""
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"

    def test_member_input_flags(self):
        """Test that we can manipulate the mutable, strict, etc. flags (see SymbolicInput) of
        Method inputs"""
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"

    def test_member_output_flags(self):
        """Test that we can manipulate the output flags (just 'borrow' I think, see SymbolicOutput)
        of Method outputs"""
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"

    def test_sanity_check_mode(self):
        """Test that Module.make(self) can take the same list of Modes that function can, so we can
        debug modules"""
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"

    def test_member_value(self):
        """Test that module Members of Value work correctly. As Result?"""
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"

    def test_member_constant(self):
        """Test that module Members of Constant work correctly.
        As Result with more optimization?"""
        print >> sys.stderr, "WARNING MODULE TEST NOT IMPLEMENTED"

