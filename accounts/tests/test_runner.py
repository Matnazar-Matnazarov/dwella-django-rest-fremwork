from django.test.runner import DiscoverRunner
from django.utils.termcolors import colorize
from django.test.runner import RemoteTestResult
import sys
import time


class ColoredTestRunner(DiscoverRunner):
    """
    Test runner that shows colored and formatted output for each test.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_count = 0
        self.test_failures = 0
        self.test_errors = 0
        self.start_time = None

    def run_suite(self, suite, **kwargs):
        """
        Run the test suite and return the result.
        """
        result = super().run_suite(suite, **kwargs)
        self.test_count = result.testsRun
        self.test_failures = len(result.failures)
        self.test_errors = len(result.errors)
        return result

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        """
        Run the test suite and print the results.
        """
        self.start_time = time.time()
        
        # Header
        print("\n" + "=" * 80)
        print(colorize("🚀 Running tests...", fg="cyan", opts=("bold",)))
        print("=" * 80 + "\n")

        result = super().run_tests(test_labels)
        
        # Footer
        duration = time.time() - self.start_time
        print("\n" + "=" * 80)
        
        if self.test_failures == 0 and self.test_errors == 0:
            print(colorize("✨ Test Results:", fg="green", opts=("bold",)))
            print(colorize(f"✓ All {self.test_count} tests passed successfully!", fg="green"))
            print(colorize(f"⏱ Total time: {duration:.2f} seconds", fg="cyan"))
        else:
            print(colorize("❌ Test Results:", fg="red", opts=("bold",)))
            print(colorize(f"✗ Tests completed with:", fg="red"))
            print(colorize(f"  • {self.test_failures} failures", fg="red") if self.test_failures else "")
            print(colorize(f"  • {self.test_errors} errors", fg="red") if self.test_errors else "")
            print(colorize(f"⏱ Total time: {duration:.2f} seconds", fg="cyan"))
        
        print("=" * 80 + "\n")
        return result

    def _makeResult(self):
        """
        Create a custom test result object.
        """
        return ColoredTestResult(self.verbosity, self.interactive, self.tb_locals)

    def _handle_test_result(self, result):
        """
        Handle the test result and print the output.
        """
        if result.wasSuccessful():
            print(colorize("OK", fg="green", opts=("bold",)))
        else:
            print(colorize("FAILED", fg="red", opts=("bold",)))


class ColoredTestResult(RemoteTestResult):
    """
    Custom test result that shows colored output for each test.
    """
    def addSuccess(self, test):
        """
        Called when a test passes.
        """
        super().addSuccess(test)
        test_name = self._get_test_name(test)
        print(colorize(f"✓ {test_name} - OK", fg="green"))

    def addError(self, test, err):
        """
        Called when a test raises an exception.
        """
        super().addError(test, err)
        test_name = self._get_test_name(test)
        print(colorize(f"✗ {test_name} - ERROR", fg="red"))
        print(colorize(f"  {str(err[1])}", fg="red"))

    def addFailure(self, test, err):
        """
        Called when a test fails.
        """
        super().addFailure(test, err)
        test_name = self._get_test_name(test)
        print(colorize(f"✗ {test_name} - FAILED", fg="red"))
        print(colorize(f"  {str(err[1])}", fg="red"))

    def _get_test_name(self, test):
        """
        Get the name of the test.
        """
        test_name = test._testMethodName
        test_doc = test._testMethodDoc
        if test_doc:
            test_name = f"{test_name} ({test_doc})"
        return f"{test.__class__.__name__}.{test_name}" 