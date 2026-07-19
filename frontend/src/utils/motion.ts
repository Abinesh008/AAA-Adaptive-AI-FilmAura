import { Variants } from "framer-motion";

export const transitionSpring = {
  type: "spring",
  stiffness: 100,
  damping: 15,
} as const;

export const transitionSmooth = {
  type: "tween",
  ease: "easeInOut",
  duration: 0.35,
} as const;

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: transitionSmooth,
  },
};

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitionSpring,
  },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transitionSpring,
  },
};

export const staggerContainer = (staggerChildren = 0.1, delayChildren = 0.0): Variants => ({
  hidden: {},
  visible: {
    transition: {
      staggerChildren,
      delayChildren,
    },
  },
});
