#include "Quaternion.h"


/****************************************************************
*																*
*		    Quaternion member functions							*
*																*
****************************************************************/

// CONSTRUCTORS

Quaternion::Quaternion()
{
}

Quaternion::Quaternion(const float w, const float x, const float y, const float z)
{
	n[VW] = w; n[VX] = x; n[VY] = y; n[VZ] = z;
}

Quaternion::Quaternion(const Quaternion& q)
{
	n[VW] = q.n[VW]; n[VX] = q.n[VX]; n[VY] = q.n[VY]; n[VZ] = q.n[VZ];
}

// Static functions

float Quaternion::Dot(const Quaternion& q0, const Quaternion& q1)
{
	return q0.n[VW] * q1.n[VW] + q0.n[VX] * q1.n[VX] + q0.n[VY] * q1.n[VY] + q0.n[VZ] * q1.n[VZ];
}

Quaternion Quaternion::UnitInverse(const Quaternion& q)
{
	return Quaternion(q.n[VW], -q.n[VX], -q.n[VY], -q.n[VZ]);
}

float Quaternion::CounterWarp(float t, float fCos)
{
	const float ATTENUATION = 0.82279687f;
	const float WORST_CASE_SLOPE = 0.58549219f;

	float fFactor = 1.0f - ATTENUATION * fCos;
	fFactor *= fFactor;
	float fK = WORST_CASE_SLOPE * fFactor;

	return t * (fK * t * (2.0f * t - 3.0f) + 1.0f + fK);
}

static const float ISQRT_NEIGHBORHOOD = 0.959066f;
static const float ISQRT_SCALE = 1.000311f;
static const float ISQRT_ADDITIVE_CONSTANT = ISQRT_SCALE / (float)sqrt(ISQRT_NEIGHBORHOOD);
static const float ISQRT_FACTOR = ISQRT_SCALE * (-0.5f / (ISQRT_NEIGHBORHOOD * (float)sqrt(ISQRT_NEIGHBORHOOD)));
float Quaternion::ISqrt_approx_in_neighborhood(float s)
{
	return ISQRT_ADDITIVE_CONSTANT + (s - ISQRT_NEIGHBORHOOD) * ISQRT_FACTOR;	
}

// Assignment operators

Quaternion& Quaternion::operator = (const Quaternion& q)
{
	n[VW] = q.n[VW]; n[VX] = q.n[VX]; n[VY] = q.n[VY]; n[VZ] = q.n[VZ];
	return *this;
}

Quaternion& Quaternion::operator += (const Quaternion& q)
{
	n[VW] += q.n[VW]; n[VX] += q.n[VX]; n[VY] += q.n[VY]; n[VZ] += q.n[VZ];
	return *this;
}

Quaternion& Quaternion::operator -= (const Quaternion& q)
{
	n[VW] -= q.n[VW]; n[VX] -= q.n[VX]; n[VY] -= q.n[VY]; n[VZ] -= q.n[VZ];
	return *this;
}

Quaternion& Quaternion::operator *= (const Quaternion& q)
{
	*this = Quaternion(n[VW] * q.n[VW] - n[VX] * q.n[VX] - n[VY] * q.n[VY] - n[VZ] * q.n[VZ],
		n[VW] * q.n[VX] + n[VX] * q.n[VW] + n[VY] * q.n[VZ] - n[VZ] * q.n[VY],
		n[VW] * q.n[VY] + n[VY] * q.n[VW] + n[VZ] * q.n[VX] - n[VX] * q.n[VZ],
		n[VW] * q.n[VZ] + n[VZ] * q.n[VW] + n[VX] * q.n[VY] - n[VY] * q.n[VX]);
	return *this;
}

Quaternion& Quaternion::operator *= (const float d)
{
	n[VW] *= d; n[VX] *= d;	n[VY] *= d; n[VZ] *= d;
	return *this;
}

Quaternion& Quaternion::operator /= (const float d)
{
	n[VW] /= d; n[VX] /= d;	n[VY] /= d; n[VZ] /= d;
	return *this;
}

// Indexing
float& Quaternion::operator [](int i)
{
	return n[i];
}

float Quaternion::operator [](int i) const
{
	return n[i];
}

float& Quaternion::W()
{
	return n[VW];
}

float Quaternion::W() const
{
	return n[VW];
}

float& Quaternion::X()
{
	return n[VX];
}

float Quaternion::X() const
{
	return n[VX];
}

float& Quaternion::Y()
{
	return n[VY];
}

float Quaternion::Y() const
{
	return n[VY];
}

float& Quaternion::Z()
{
	return n[VZ];
}

float Quaternion::Z() const
{
	return n[VZ];
}

// Friends

Quaternion operator - (const Quaternion& q)
{
	return Quaternion(-q.n[VW], -q.n[VX], -q.n[VY], -q.n[VZ]); 
}

Quaternion operator + (const Quaternion& q0, const Quaternion& q1)
{
	return Quaternion(q0.n[VW] + q1.n[VW], q0.n[VX] + q1.n[VX], q0.n[VY] + q1.n[VY], q0.n[VZ] + q1.n[VZ]);
}

Quaternion operator - (const Quaternion& q0, const Quaternion& q1)
{
	return Quaternion(q0.n[VW] - q1.n[VW], q0.n[VX] - q1.n[VX], q0.n[VY] - q1.n[VY], q0.n[VZ] - q1.n[VZ]);
}

Quaternion operator * (const Quaternion& q, const float d)
{
	return Quaternion(q.n[VW] * d, q.n[VX] * d, q.n[VY] * d, q.n[VZ] * d);
}

Quaternion operator * (const float d, const Quaternion& q)
{
	return Quaternion(q.n[VW] * d, q.n[VX] * d, q.n[VY] * d, q.n[VZ] * d);
}

Quaternion operator * (const Quaternion& q0, const Quaternion& q1)
{
	return Quaternion(q0.n[VW] * q1.n[VW] - q0.n[VX] * q1.n[VX] - q0.n[VY] * q1.n[VY] - q0.n[VZ] * q1.n[VZ],
		q0.n[VW] * q1.n[VX] + q0.n[VX] * q1.n[VW] + q0.n[VY] * q1.n[VZ] - q0.n[VZ] * q1.n[VY],
		q0.n[VW] * q1.n[VY] + q0.n[VY] * q1.n[VW] + q0.n[VZ] * q1.n[VX] - q0.n[VX] * q1.n[VZ],
		q0.n[VW] * q1.n[VZ] + q0.n[VZ] * q1.n[VW] + q0.n[VX] * q1.n[VY] - q0.n[VY] * q1.n[VX]);
}

Quaternion operator / (const Quaternion& q, const float d)
{
	return Quaternion(q.n[VW] / d, q.n[VX] / d, q.n[VY] / d, q.n[VZ] / d);
}

bool operator == (const Quaternion& q0, const Quaternion& q1)
{
	return (q0.n[VW] == q1.n[VW]) && (q0.n[VX] == q1.n[VX]) && (q0.n[VY] == q1.n[VY]) && (q0.n[VZ] == q1.n[VZ]);
}

bool operator != (const Quaternion& q0, const Quaternion& q1)
{
	return !(q0 == q1); 
}

// special functions

float Quaternion::SqrLength() const
{
	return n[VW] * n[VW] + n[VX] * n[VX] + n[VY] * n[VY] + n[VZ] * n[VZ];
}

float Quaternion::Length() const
{
	return sqrt(SqrLength());
}

Quaternion& Quaternion::Normalize()
{
	float l = Length();
	if (l < EPSILON || abs(l) > 1e6)
	{
		FromAxisAngle(axisY, 0.0f);
	}else
	{
		*this /= l;
	}

	return *this; 
}

Quaternion& Quaternion::FastNormalize() 
{
	float s = n[VW] * n[VW] + n[VX] * n[VX] + n[VY] * n[VY] + n[VZ] * n[VZ]; // length^2
	float k = ISqrt_approx_in_neighborhood(s);

	if (s <= 0.91521198) {
		k *= ISqrt_approx_in_neighborhood(k * k * s);

		if (s <= 0.65211970) {
			k *= ISqrt_approx_in_neighborhood(k * k * s);
		}
	}

	n[VW] *= k;
	n[VX] *= k;
	n[VY] *= k;
	n[VZ] *= k;

	return * this;
}

Quaternion Quaternion::Inverse() const
{
	return Quaternion(n[VW], -n[VX], -n[VY], -n[VZ]);
}

Quaternion Quaternion::Exp(const Quaternion& q)
{
	// q = A*(x*i+y*j+z*k) where (x,y,z) is unit length
	// exp(q) = cos(A)+sin(A)*(x*i+y*j+z*k)
	float angle = sqrt(q.n[VX] * q.n[VX] + q.n[VY] * q.n[VY] + q.n[VZ] * q.n[VZ]);
	float sn, cs;
	sn = sin(angle);
	cs = cos(angle);

	// When A is near zero, sin(A)/A is approximately 1.  Use
	// exp(q) = cos(A)+A*(x*i+y*j+z*k)
	float coeff = ( abs(sn) < EPSILON ? 1.0f : sn/angle );

	Quaternion result(cs, coeff * q.n[VX], coeff * q.n[VY], coeff * q.n[VZ]);

	return result;
}

Quaternion Quaternion::Log(const Quaternion& q)
{
	// q = cos(A)+sin(A)*(x*i+y*j+z*k) where (x,y,z) is unit length
	// log(q) = A*(x*i+y*j+z*k)

	float angle = acos(q.n[VW]);
	float sn = sin(angle);

	// When A is near zero, A/sin(A) is approximately 1.  Use
	// log(q) = sin(A)*(x*i+y*j+z*k)
	float coeff = ( abs(sn) < EPSILON ? 1.0f : angle/sn );

	return Quaternion(0.0f, coeff * q.n[VX], coeff * q.n[VY], coeff * q.n[VZ]);
}

void Quaternion::Zero()
{
	n[VW] = n[VX] = n[VY] = n[VZ] = 0.0f;
}

// Conversion functions
void Quaternion::ToAxisAngle (vec3& axis, float& angleRad) const
{
	//float fLength = Length();
	vec3 v(n[VX], n[VY], n[VZ]);
	float fLength = v.Length();

	if ( fLength < EPSILON )
	{
		angleRad = 0;
		axis[VX] = 0;
		axis[VY] = 0;
		axis[VZ] = 0;
	}
	else
	{
		angleRad = 2.0f * acos(n[VW]);
		float invLength = 1.0f / fLength;
		axis[VX] = n[VX] * invLength;
		axis[VY] = n[VY] * invLength;
		axis[VZ] = n[VZ] * invLength;
	}
}

void Quaternion::FromAxisAngle (const vec3& axis, float angleRad)
{
	float fHalfAngle = angleRad * 0.5f;
	float sn = sin(fHalfAngle);
	n[VW] = cos(fHalfAngle);
	n[VX] = axis[VX] * sn;
	n[VY] = axis[VY] * sn;
	n[VZ] = axis[VZ] * sn;
}


math::RotationMatrix<float> Quaternion::toRotationMatrix() {
	float s, x, y, z;
	s = W(); x = X(); y = Y(); z = Z();
	vec3 v1(1-2*(y*y+z*z), 2*(x*y-s*z), 2*(x*z+s*y));
	vec3 v2(2*(x*y+s*z), 1-2*(x*x+z*z), 2*(y*z-s*x));
	vec3 v3(2*(x*z-s*y), 2*(y*z+s*x), 1-2*(x*x+y*y));
	math::RotationMatrix<float> mat(v1,v2,v3);
	return mat;
}