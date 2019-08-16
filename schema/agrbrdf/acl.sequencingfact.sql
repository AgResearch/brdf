--
-- Name: sequencingfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE sequencingfact FROM PUBLIC;
REVOKE ALL ON TABLE sequencingfact FROM agrbrdf;
GRANT ALL ON TABLE sequencingfact TO agrbrdf;
GRANT SELECT ON TABLE sequencingfact TO gbs;


