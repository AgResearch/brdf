--
-- Name: biosamplefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplefact FROM PUBLIC;
REVOKE ALL ON TABLE biosamplefact FROM agrbrdf;
GRANT ALL ON TABLE biosamplefact TO agrbrdf;
GRANT SELECT ON TABLE biosamplefact TO gbs;


