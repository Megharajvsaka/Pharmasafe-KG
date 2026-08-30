/**
 * PharmaSafe-KG — Framer Motion Animation Variants
 * Professional, subtle, and accessible transitions.
 */

import { Variants, Transition } from "framer-motion";

export const transitions: Record<string, Transition> = {
  default: { duration: 0.25, ease: "easeOut" },
  fast: { duration: 0.15, ease: "easeOut" },
  smooth: { duration: 0.35, ease: "easeInOut" },
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: transitions.default,
  },
};

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.default,
  },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.05,
    },
  },
};

export const cardItem: Variants = {
  hidden: { opacity: 0, y: 8 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.default,
  },
};

export const scaleUp: Variants = {
  hidden: { opacity: 0, scale: 0.98 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transitions.fast,
  },
};

export const buttonPress = {
  tap: { scale: 0.98 },
};

export const subtleHover = {
  hover: { y: -1, transition: transitions.fast },
};
