import { functionToTest } from '../src/someFile';
import { renderImage, fetchUserData } from '../src/userInterface';

// Welcome message for developers
console.log('🚀 Welcome to the test suite! Let\'s ensure our code is rock-solid! 🧪');

describe('Core Functionality Tests', () => {
  describe('functionToTest', () => {
    test('should return expected result for valid input', () => {
      const input = 'some input';
      const expectedOutput = 'expected output';
      expect(functionToTest(input)).toBe(expectedOutput);
    });

    test('should throw an error for invalid input', () => {
      const invalidInput = null;
      expect(() => functionToTest(invalidInput)).toThrow('Invalid input');
    });

    test('should handle edge cases', () => {
      expect(functionToTest('')).toBe('');
      expect(functionToTest(' ')).toBe(' ');
      expect(functionToTest('123')).toBe('123');
    });
  });
});

describe('User Interface Tests', () => {
  describe('renderImage', () => {
    test('should render image with correct attributes', () => {
      const imageUrl = 'https://example.com/image.jpg';
      const altText = 'A beautiful landscape';
      const renderedImage = renderImage(imageUrl, altText);
      
      expect(renderedImage).toContain(`src="${imageUrl}"`);
      expect(renderedImage).toContain(`alt="${altText}"`);
    });

    test('should apply lazy loading to images', () => {
      const imageUrl = 'https://example.com/image.jpg';
      const renderedImage = renderImage(imageUrl);
      
      expect(renderedImage).toContain('loading="lazy"');
    });
  });

  describe('fetchUserData', () => {
    test('should fetch user data successfully', async () => {
      const mockUser = { id: 1, name: 'John Doe', avatar: 'https://example.com/avatar.jpg' };
      global.fetch = jest.fn(() =>
        Promise.resolve({
          json: () => Promise.resolve(mockUser),
        })
      );

      const userData = await fetchUserData(1);
      expect(userData).toEqual(mockUser);
    });

    test('should handle fetch errors gracefully', async () => {
      global.fetch = jest.fn(() => Promise.reject('API is down'));

      await expect(fetchUserData(1)).rejects.toThrow('Failed to fetch user data');
    });
  });
});

// Cleanup and farewell message
afterAll(() => {
  console.log('✨ All tests completed! Thanks for keeping our code quality high! 🏆');
});
