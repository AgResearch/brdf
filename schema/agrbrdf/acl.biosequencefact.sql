--
-- Name: biosequencefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosequencefact FROM PUBLIC;
REVOKE ALL ON TABLE biosequencefact FROM agrbrdf;
GRANT ALL ON TABLE biosequencefact TO agrbrdf;
GRANT SELECT ON TABLE biosequencefact TO gbs;


