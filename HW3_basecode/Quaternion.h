#pragma once

#include <iostream>
#include <assert.h>
#include <cmath>
#include "vec.h"
#include "matrix.h"

using namespace std;

#ifndef EPSILON
	#define EPSILON 0.001
#endif

// min-max macros
#define MIN(A,B) ((A) < (B) ? (A) : (B))
#define MAX(A,B) ((A) > (B) ? (A) : (B))

// error handling macro
#define ALGEBRA_ERROR(E) { assert(false); }

/****************************************************************
*																*
*		    Quaternion          								*
*																*
****************************************************************/


class Quaternion
{
protected:

	float n[4];

	// Used by Slerp
	static float CounterWarp(float t, float fCos);
	static float ISqrt_approx_in_neighborhood(float s);

	// Internal indexing
	float& operator[](int i);
	float operator[](int i) const;
public:

	// Constructors
	Quaternion();
	Quaternion(const float w, const float x, const float y, const float z);
	Quaternion(const Quaternion& q);

	// Static functions
	static float Dot(const Quaternion& q0, const Quaternion& q1);
	static Quaternion Exp(const Quaternion& q);
	static Quaternion Log(const Quaternion& q);
	static Quaternion UnitInverse(const Quaternion& q);
	static Quaternion Slerp(float t, const Quaternion& q0, const Quaternion& q1);
	static Quaternion Intermediate (const Quaternion& q0, const Quaternion& q1, const Quaternion& q2);
	static Quaternion Squad(float t, const Quaternion& q0, const Quaternion& a, const Quaternion& b, const Quaternion& q1);

	// Conversion functions
	void ToAxisAngle (vec3& axis, float& angleRad) const;
	void FromAxisAngle (const vec3& axis, float angleRad);
	mat3 ToRotation() const;
	void FromRotation (const mat3& rot);

	math::RotationMatrix<float> toRotationMatrix();

	// Assignment operators
	Quaternion& operator = (const Quaternion& q);	// assignment of a quaternion
	Quaternion& operator += (const Quaternion& q);	// summation with a quaternion
	Quaternion& operator -= (const Quaternion& q);	// subtraction with a quaternion
	Quaternion& operator *= (const Quaternion& q);	// multiplication by a quaternion
	Quaternion& operator *= (const float d);		// multiplication by a scalar
	Quaternion& operator /= (const float d);		// division by a scalar

	// Indexing
	float& W();
	float W() const;
	float& X();
	float X() const;
	float& Y();
	float Y() const;
	float& Z();
	float Z() const;

	// Friends
	friend Quaternion operator - (const Quaternion& q);							// -q
	friend Quaternion operator + (const Quaternion& q0, const Quaternion& q1);	// q0 + q1
	friend Quaternion operator - (const Quaternion& q0, const Quaternion& q1);	// q0 - q1
	friend Quaternion operator * (const Quaternion& q, const float d);			// q * 3.0
	friend Quaternion operator * (const float d, const Quaternion& q);			// 3.0 * v
	friend Quaternion operator * (const Quaternion& q0, const Quaternion& q1);  // q0 * q1
	friend Quaternion operator / (const Quaternion& q, const float d);			// q / 3.0
	friend bool operator == (const Quaternion& q0, const Quaternion& q1);		// q0 == q1 ?
	friend bool operator != (const Quaternion& q0, const Quaternion& q1);		// q0 != q1 ?

	// Special functions
	float Length() const;
	float SqrLength() const;
	Quaternion& Normalize();
	Quaternion& FastNormalize();
	Quaternion Inverse() const;
	void Zero();

	//friend mat3;
};