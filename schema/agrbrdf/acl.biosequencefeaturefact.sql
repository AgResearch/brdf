--
-- Name: biosequencefeaturefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosequencefeaturefact FROM PUBLIC;
REVOKE ALL ON TABLE biosequencefeaturefact FROM agrbrdf;
GRANT ALL ON TABLE biosequencefeaturefact TO agrbrdf;
GRANT SELECT ON TABLE biosequencefeaturefact TO gbs;


