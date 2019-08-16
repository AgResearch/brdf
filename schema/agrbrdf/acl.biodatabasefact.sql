--
-- Name: biodatabasefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biodatabasefact FROM PUBLIC;
REVOKE ALL ON TABLE biodatabasefact FROM agrbrdf;
GRANT ALL ON TABLE biodatabasefact TO agrbrdf;
GRANT SELECT ON TABLE biodatabasefact TO gbs;


